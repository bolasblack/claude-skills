import { spawnSync } from 'node:child_process'
import {
  existsSync,
  readdirSync,
  readFileSync,
  realpathSync,
  statSync,
} from 'node:fs'
import { basename, dirname, extname, join, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

type GuardrailsResult = {
  exitCode: number
  stdout: string
  stderr: string
}

type Environment = Record<string, string | undefined>

type RunGuardrailsInput = {
  args: string[]
  cwd?: string
  env?: Environment
  instructionsDir?: string
}

type Enforcement = {
  review: boolean
  lint: string[]
}

type RuleMetadata = {
  number: string
  short: string
  enforcement: Enforcement
  references?: string[]
  skip_index_reason?: string
  lint_assist_reason?: string
  retire_reason?: string
}

type RuleRecord = {
  id: string
  path: string
  body: string
  metadata: RuleMetadata
  retired: boolean
}

type ReviewMetadataInstruction = {
  key: string
  title: string
  paths: string[]
  body: string
}

type ChangedRuleSnapshot = {
  current?: RuleRecord
  base?: RuleRecord
  parseErrors: string[]
}

type ParsedReference = {
  path: string
  lineRange?: {
    start: number
    end: number
  }
}

const guardrailsDir = '.agents/guardrails'
const rulesDir = `${guardrailsDir}/rules`
const retiredRulesDir = `${guardrailsDir}/retired-rules`
const indexPath = `${guardrailsDir}/index.md`
const ruleFilePattern = /^GRL-\d+\.md$/
const ruleIdPattern = /^GRL-\d+$/
const ruleIdPrefix = 'GRL-'
const ruleTokenPattern = /GRL-\d+/g
const fencePattern = /^ {0,3}(`{3,}|~{3,})(.*)$/
const reviewMetadataPathPattern = new RegExp(
  `^(?:${escapeRegExp(rulesDir)}|${escapeRegExp(retiredRulesDir)})/GRL-\\d+\\.md$`,
)
const defaultReviewMetadataInstructionsDir = join(
  dirname(fileURLToPath(import.meta.url)),
  '..',
  'references',
  'review-metadata-instructions',
)
const expectedReviewInstructionKeys = [
  'active-rule-removed',
  'enforcement',
  'lint-assist-reason',
  'parse-issue',
  'references',
  'retire-reason',
  'retired-rule-text',
  'router',
  'rule-text',
  'skip-index-reason',
] as const
const activeRuleFieldInstructionKeys = [
  ['enforcement', 'enforcement'],
  ['skip_index_reason', 'skip-index-reason'],
  ['lint_assist_reason', 'lint-assist-reason'],
  ['references', 'references'],
] as const satisfies readonly (readonly [
  keyof RuleMetadata,
  (typeof expectedReviewInstructionKeys)[number],
])[]

export async function runGuardrails(
  input: RunGuardrailsInput,
): Promise<GuardrailsResult> {
  if (typeof (globalThis as { Bun?: unknown }).Bun === 'undefined') {
    return {
      exitCode: 1,
      stdout: '',
      stderr:
        'guardrails requires the Bun runtime. Install Bun from https://bun.sh, then run: bun <skill-path>/scripts/guardrails.ts <command>\n',
    }
  }

  const startDir = input.cwd ?? process.cwd()
  const env = input.env ?? process.env

  try {
    const { rootOption, rest } = extractRootOption(input.args)
    const [command, ...args] = rest
    const root = resolveRoot(startDir, rootOption, env)

    if (command === 'validate') {
      validateGuardrails(root)
      return { exitCode: 0, stdout: 'Guardrail validation OK.\n', stderr: '' }
    }

    if (command === 'render') {
      return { exitCode: 0, stdout: renderGuardrails(root, args), stderr: '' }
    }

    if (command === 'review-metadata') {
      const result = reviewMetadata(
        root,
        args,
        env,
        input.instructionsDir ?? defaultReviewMetadataInstructionsDir,
      )
      return { exitCode: 0, stdout: result.stdout, stderr: result.stderr }
    }

    if (command === 'next-id') {
      return { exitCode: 0, stdout: `${nextId(root)}\n`, stderr: '' }
    }

    return {
      exitCode: 1,
      stdout: '',
      stderr: `Unknown command: ${command ?? '(missing)'}\n`,
    }
  } catch (error) {
    return {
      exitCode: 1,
      stdout: '',
      stderr: `${error instanceof Error ? error.message : String(error)}\n`,
    }
  }
}

function extractRootOption(args: string[]): {
  rootOption?: string
  rest: string[]
} {
  const rest: string[] = []
  let rootOption: string | undefined

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index]

    if (arg === '--root') {
      const value = args[index + 1]

      if (!value) {
        throw new Error('--root requires a directory')
      }

      rootOption = value
      index += 1
      continue
    }

    if (arg.startsWith('--root=')) {
      const value = arg.slice('--root='.length)

      if (!value) {
        throw new Error('--root requires a directory')
      }

      rootOption = value
      continue
    }

    rest.push(arg)
  }

  return { rootOption, rest }
}

function resolveRoot(
  startDir: string,
  override: string | undefined,
  env: Environment,
): string {
  if (override) {
    return resolve(startDir, override)
  }

  const environmentRoot = env.GUARDRAILS_ROOT

  if (environmentRoot && environmentRoot.trim().length > 0) {
    return resolve(startDir, environmentRoot.trim())
  }

  let current = resolve(startDir)

  while (true) {
    if (existsSync(join(current, guardrailsDir))) {
      return current
    }

    const parent = dirname(current)

    if (parent === current) {
      break
    }

    current = parent
  }

  const result = spawnSync('git', ['rev-parse', '--show-toplevel'], {
    cwd: startDir,
    encoding: 'utf8',
  })

  if (result.status === 0) {
    const top = result.stdout.trim()

    if (top) {
      return top
    }
  }

  return resolve(startDir)
}

function validateGuardrails(root: string): void {
  const errors: string[] = []
  const indexAbsolutePath = repoPath(root, indexPath)
  const rulesAbsoluteDir = repoPath(root, rulesDir)

  if (!existsSync(indexAbsolutePath)) {
    errors.push(`missing required file: ${indexPath}`)
  }

  if (
    !existsSync(rulesAbsoluteDir) ||
    !statSync(rulesAbsoluteDir).isDirectory()
  ) {
    errors.push(`missing required directory: ${rulesDir}`)
  }

  const indexIds = existsSync(indexAbsolutePath)
    ? scanIndexIds(readFile(indexAbsolutePath))
    : new Set<string>()
  const collection = readRuleCollection(root, errors)

  validateDuplicateIds(collection, errors)
  validateIndexReferences(indexIds, collection, errors)

  for (const rule of collection.active) {
    validateBaseRule(root, rule, errors)
    validateActiveRule(rule, indexIds, errors)
  }

  for (const rule of collection.retired) {
    validateBaseRule(root, rule, errors)
    validateRetiredRule(rule, indexIds, errors)
  }

  if (errors.length > 0) {
    throw new Error(
      `Guardrail validation failed:\n${errors.map(error => `- ${error}`).join('\n')}`,
    )
  }
}

function renderGuardrails(root: string, args: string[]): string {
  const detail = args.includes('--detail')
  const ids = uniqueStrings(args.filter(arg => arg !== '--detail'))

  if (ids.length === 0) {
    throw new Error('render requires at least one explicit GRL ID')
  }

  const errors: string[] = []
  const collection = readRuleCollection(root, errors)

  if (errors.length > 0) {
    throw new Error(
      `Cannot render guardrails:\n${errors.map(error => `- ${error}`).join('\n')}`,
    )
  }

  const activeById = new Map(collection.active.map(rule => [rule.id, rule]))
  const retiredById = new Map(collection.retired.map(rule => [rule.id, rule]))
  const sections: string[] = ['# Guardrails']

  for (const id of ids) {
    if (!ruleIdPattern.test(id)) {
      throw new Error(`render accepts only explicit GRL IDs: ${id}`)
    }

    const retiredRule = retiredById.get(id)
    if (retiredRule) {
      throw new Error(
        `Cannot render retired ${id}: ${retiredRule.metadata.retire_reason ?? 'missing retire_reason'}`,
      )
    }

    const rule = activeById.get(id)
    if (!rule) {
      throw new Error(`Unknown GRL ID: ${id}`)
    }

    sections.push(renderRule(rule, detail))
  }

  return `${sections.join('\n\n')}\n`
}

function reviewMetadata(
  root: string,
  args: string[],
  env: Environment,
  instructionsDir: string,
): { stdout: string; stderr: string } {
  const { base, usedHeadFallback } = resolveBaseRef(root, args, env)
  const stderr = usedHeadFallback
    ? 'No --base given and origin/HEAD is not configured; comparing against HEAD.\n'
    : ''
  const pathspecs = [
    indexPath,
    `${rulesDir}/GRL-*.md`,
    `${retiredRulesDir}/GRL-*.md`,
  ]

  requireGitRoot(root)
  requireBaseRef(root, base)

  const changedPaths = gitLines(root, [
    'diff',
    '--name-only',
    '--no-renames',
    base,
    '--',
    ...pathspecs,
  ])
  const untrackedPaths = gitLines(root, [
    'ls-files',
    '--others',
    '--exclude-standard',
    '--',
    ...pathspecs,
  ])
  const paths = uniqueStrings([...changedPaths, ...untrackedPaths]).filter(
    isReviewMetadataPath,
  )

  if (paths.length === 0) {
    return {
      stdout: 'No changed GRL files or guardrail router changes.\n',
      stderr,
    }
  }

  return {
    stdout: buildReviewMetadataInstructions(
      root,
      base,
      paths,
      instructionsDir,
    ).join('\n'),
    stderr,
  }
}

function resolveBaseRef(
  root: string,
  args: string[],
  env: Environment,
): { base: string; usedHeadFallback: boolean } {
  const explicitBase = readBaseOption(args)

  if (explicitBase) {
    return { base: explicitBase, usedHeadFallback: false }
  }

  const environmentBase = env.GUARDRAILS_BASE

  if (environmentBase && environmentBase.trim().length > 0) {
    return { base: environmentBase.trim(), usedHeadFallback: false }
  }

  const result = spawnSync(
    'git',
    ['symbolic-ref', '--short', 'refs/remotes/origin/HEAD'],
    { cwd: root, encoding: 'utf8' },
  )

  if (result.status === 0) {
    const originHead = result.stdout.trim()

    if (originHead) {
      return { base: originHead, usedHeadFallback: false }
    }
  }

  return { base: 'HEAD', usedHeadFallback: true }
}

function readBaseOption(args: string[]): string | undefined {
  const baseIndex = args.indexOf('--base')

  if (baseIndex >= 0) {
    const value = args[baseIndex + 1]

    if (!value) {
      throw new Error('review-metadata --base requires a base ref')
    }

    return value
  }

  const inlineBase = args.find(arg => arg.startsWith('--base='))

  if (inlineBase !== undefined) {
    const value = inlineBase.slice('--base='.length)

    if (!value) {
      throw new Error('review-metadata --base requires a base ref')
    }

    return value
  }

  return undefined
}

function requireGitRoot(root: string): void {
  const result = spawnSync('git', ['rev-parse', '--show-toplevel'], {
    cwd: root,
    encoding: 'utf8',
  })

  if (result.status !== 0) {
    throw new Error('review-metadata requires running inside a git repository.')
  }

  const top = result.stdout.trim()

  if (realpathSync(top) !== realpathSync(root)) {
    throw new Error(
      `review-metadata requires the guardrails root to match the git repository root (guardrails root: ${root}, git root: ${top})`,
    )
  }
}

function requireBaseRef(root: string, base: string): void {
  const result = spawnSync(
    'git',
    ['rev-parse', '--verify', '--quiet', `${base}^{commit}`],
    { cwd: root, encoding: 'utf8' },
  )

  if (result.status !== 0) {
    throw new Error(
      `Base ref not found: ${base}. Pass --base <ref> or set GUARDRAILS_BASE.`,
    )
  }
}

function gitLines(root: string, args: string[]): string[] {
  const result = spawnSync('git', args, { cwd: root, encoding: 'utf8' })

  if (result.status !== 0) {
    throw new Error(result.stderr.trim() || `git ${args[0]} failed`)
  }

  return result.stdout
    .split('\n')
    .map(line => line.trim())
    .filter(Boolean)
}

function isReviewMetadataPath(path: string): boolean {
  return path === indexPath || reviewMetadataPathPattern.test(path)
}

function buildReviewMetadataInstructions(
  root: string,
  base: string,
  paths: string[],
  instructionsDir: string,
): string[] {
  const catalog = readReviewInstructionCatalog(instructionsDir)
  const instructions = new Map<string, ReviewMetadataInstruction>()
  const changedPaths = new Set(paths)

  for (const path of paths) {
    if (path === indexPath) {
      addReviewInstruction(instructions, catalog, 'router', path)
      continue
    }

    const retired = path.startsWith(`${retiredRulesDir}/`)
    const snapshot = readChangedRuleSnapshot(root, base, path, retired)

    if (retired) {
      if (
        !snapshot.base ||
        hasMetadataFieldChanged(snapshot, 'retire_reason')
      ) {
        addReviewInstruction(instructions, catalog, 'retire-reason', path)
      }

      if (
        hasRuleBodyChanged(snapshot) ||
        hasMetadataFieldChanged(snapshot, 'short')
      ) {
        addReviewInstruction(instructions, catalog, 'retired-rule-text', path)
      }
    } else if (!snapshot.current && snapshot.base) {
      if (!hasRetiredCounterpart(root, changedPaths, path)) {
        addReviewInstruction(instructions, catalog, 'active-rule-removed', path)
      }
    } else {
      for (const [field, key] of activeRuleFieldInstructionKeys) {
        if (hasMetadataFieldChanged(snapshot, field)) {
          addReviewInstruction(instructions, catalog, key, path)
        }
      }

      if (
        hasMetadataFieldChanged(snapshot, 'short') ||
        hasRuleBodyChanged(snapshot)
      ) {
        addReviewInstruction(instructions, catalog, 'rule-text', path)
      }
    }

    for (const parseError of snapshot.parseErrors) {
      addParseErrorInstruction(instructions, catalog, path, parseError)
    }
  }

  if (instructions.size === 0) {
    return [
      'Reviewer instructions:',
      '',
      'No field-specific instruction sections matched; review changed guardrail files for schema and routing consistency.',
      '',
    ]
  }

  return [
    'Reviewer instructions:',
    '',
    ...[...instructions.values()].flatMap(instruction => {
      return [
        `## ${instruction.title}`,
        '',
        instruction.body.trim(),
        '',
        'Files:',
        ...instruction.paths.map(path => `- ${path}`),
        '',
      ]
    }),
  ]
}

function hasRetiredCounterpart(
  root: string,
  changedPaths: ReadonlySet<string>,
  activePath: string,
): boolean {
  const retiredPath = `${retiredRulesDir}/${basename(activePath)}`

  return (
    changedPaths.has(retiredPath) && existsSync(repoPath(root, retiredPath))
  )
}

function readChangedRuleSnapshot(
  root: string,
  base: string,
  path: string,
  retired: boolean,
): ChangedRuleSnapshot {
  const parseErrors: string[] = []

  return {
    current: readRuleAtWorkingTree(root, path, retired, parseErrors),
    base: readRuleAtBase(root, base, path, retired, parseErrors),
    parseErrors,
  }
}

function readRuleAtWorkingTree(
  root: string,
  path: string,
  retired: boolean,
  parseErrors: string[],
): RuleRecord | undefined {
  const absolutePath = repoPath(root, path)

  if (!existsSync(absolutePath)) {
    return undefined
  }

  try {
    return parseRuleFile(path, readFile(absolutePath), retired)
  } catch (error) {
    parseErrors.push(
      `could not parse working tree ${path}: ${error instanceof Error ? error.message : String(error)}`,
    )
    return undefined
  }
}

function readRuleAtBase(
  root: string,
  base: string,
  path: string,
  retired: boolean,
  parseErrors: string[],
): RuleRecord | undefined {
  const result = spawnSync('git', ['show', `${base}:${path}`], {
    cwd: root,
    encoding: 'utf8',
  })

  if (result.status !== 0) {
    return undefined
  }

  try {
    return parseRuleFile(path, result.stdout.replace(/\r\n/g, '\n'), retired)
  } catch (error) {
    parseErrors.push(
      `could not parse ${base}:${path}: ${error instanceof Error ? error.message : String(error)}`,
    )
    return undefined
  }
}

function hasMetadataFieldChanged(
  snapshot: ChangedRuleSnapshot,
  field: keyof RuleMetadata,
): boolean {
  if (!snapshot.current && !snapshot.base) {
    return false
  }

  return (
    stableJson(snapshot.current?.metadata[field]) !==
    stableJson(snapshot.base?.metadata[field])
  )
}

function hasRuleBodyChanged(snapshot: ChangedRuleSnapshot): boolean {
  return (
    (snapshot.current?.body ?? undefined) !== (snapshot.base?.body ?? undefined)
  )
}

function addReviewInstruction(
  instructions: Map<string, ReviewMetadataInstruction>,
  catalog: Map<string, Omit<ReviewMetadataInstruction, 'key' | 'paths'>>,
  key: string,
  path: string,
): void {
  const existing = instructions.get(key)
  const instruction = catalog.get(key)

  if (!instruction) {
    throw new Error(`Missing review metadata instruction for key: ${key}`)
  }

  if (existing) {
    existing.paths.push(path)
    return
  }

  instructions.set(key, { key, paths: [path], ...instruction })
}

function addParseErrorInstruction(
  instructions: Map<string, ReviewMetadataInstruction>,
  catalog: Map<string, Omit<ReviewMetadataInstruction, 'key' | 'paths'>>,
  path: string,
  parseError: string,
): void {
  const key = `parse-issue:${path}:${parseError}`
  const instruction = catalog.get('parse-issue')

  if (!instruction) {
    throw new Error('Missing review metadata instruction for key: parse-issue')
  }

  instructions.set(key, {
    key,
    title: instruction.title,
    paths: [path],
    body: [`- ${parseError}`, instruction.body.trim()].join('\n'),
  })
}

function readReviewInstructionCatalog(
  instructionsDir: string,
): Map<string, Omit<ReviewMetadataInstruction, 'key' | 'paths'>> {
  if (!existsSync(instructionsDir) || !statSync(instructionsDir).isDirectory()) {
    throw new Error(
      `Missing review metadata instruction directory: ${instructionsDir}`,
    )
  }

  const expectedKeys = new Set<string>(expectedReviewInstructionKeys)
  const catalog = new Map<
    string,
    Omit<ReviewMetadataInstruction, 'key' | 'paths'>
  >()

  for (const entry of readdirSync(instructionsDir).sort()) {
    const path = join(instructionsDir, entry)

    if (!statSync(path).isFile()) {
      throw new Error(`Unexpected review metadata instruction entry: ${entry}`)
    }

    if (extname(entry) !== '.md') {
      throw new Error(
        `Review metadata instruction file must be Markdown: ${entry}`,
      )
    }

    const key = basename(entry, '.md')

    if (!expectedKeys.has(key)) {
      throw new Error(`Unknown review metadata instruction key: ${key}`)
    }

    if (catalog.has(key)) {
      throw new Error(`Duplicate review metadata instruction key: ${key}`)
    }

    try {
      catalog.set(key, parseReviewInstructionFile(readFile(path)))
    } catch (error) {
      throw new Error(
        `${path}: ${error instanceof Error ? error.message : String(error)}`,
      )
    }
  }

  const missingKeys = [...expectedKeys].filter(key => !catalog.has(key))

  if (missingKeys.length > 0) {
    throw new Error(
      `Missing review metadata instruction keys: ${missingKeys.join(', ')}`,
    )
  }

  return catalog
}

function parseReviewInstructionFile(
  source: string,
): Omit<ReviewMetadataInstruction, 'key' | 'paths'> {
  const frontmatter = parseFrontmatter(source)
  const title = frontmatter.metadata.title
  const body = frontmatter.body.trim()

  if (!isNonEmptyString(title)) {
    throw new Error('title must be a non-empty string')
  }

  if (!body) {
    throw new Error('body must be non-empty')
  }

  return { title: title.trim(), body }
}

function stableJson(value: unknown): string {
  return JSON.stringify(value ?? null)
}

function nextId(root: string): string {
  const errors: string[] = []
  const collection = readRuleCollection(root, errors)

  if (errors.length > 0) {
    throw new Error(
      `Cannot calculate next GRL ID:\n${errors.map(error => `- ${error}`).join('\n')}`,
    )
  }

  const maxId = [...collection.active, ...collection.retired].reduce(
    (max, rule) => {
      return Math.max(max, ruleNumber(rule.id))
    },
    0,
  )

  return `GRL-${maxId + 1}`
}

function readRuleCollection(
  root: string,
  errors: string[],
): { active: RuleRecord[]; retired: RuleRecord[] } {
  return {
    active: readRulesFromDirectory(root, rulesDir, false, errors),
    retired: readRulesFromDirectory(root, retiredRulesDir, true, errors),
  }
}

function readRulesFromDirectory(
  root: string,
  directory: string,
  retired: boolean,
  errors: string[],
): RuleRecord[] {
  const absoluteDirectory = repoPath(root, directory)

  if (!existsSync(absoluteDirectory)) {
    return []
  }

  const rules: RuleRecord[] = []

  for (const entry of readdirSync(absoluteDirectory).sort()) {
    const path = `${directory}/${entry}`
    const absolutePath = repoPath(root, path)

    if (!statSync(absolutePath).isFile()) {
      continue
    }

    if (!ruleFilePattern.test(entry)) {
      errors.push(`rule file name must match GRL-<number>.md: ${path}`)
      continue
    }

    try {
      const parsed = parseRuleFile(path, readFile(absolutePath), retired)
      rules.push(parsed)
    } catch (error) {
      errors.push(
        `${path}: ${error instanceof Error ? error.message : String(error)}`,
      )
    }
  }

  return rules
}

function parseFrontmatter(source: string): {
  metadata: Record<string, unknown>
  body: string
} {
  if (!source.startsWith('---\n')) {
    throw new Error('missing YAML frontmatter')
  }

  const frontmatterEnd = source.indexOf('\n---', 4)

  if (frontmatterEnd < 0) {
    throw new Error('unterminated YAML frontmatter')
  }

  const parsed = Bun.YAML.parse(source.slice(4, frontmatterEnd))

  if (!isRecord(parsed)) {
    throw new Error('frontmatter must be a mapping')
  }

  return {
    metadata: parsed,
    body: source.slice(frontmatterEnd + 4).replace(/^\r?\n/, ''),
  }
}

function parseRuleFile(
  path: string,
  source: string,
  retired: boolean,
): RuleRecord {
  const { metadata: parsed, body } = parseFrontmatter(source)
  const metadata = parsed as Partial<RuleMetadata>
  const id = basename(path, '.md')

  return {
    id,
    path,
    body,
    metadata: {
      number: metadata.number as string,
      short: metadata.short as string,
      enforcement: metadata.enforcement as Enforcement,
      references: metadata.references,
      skip_index_reason: metadata.skip_index_reason,
      lint_assist_reason: metadata.lint_assist_reason,
      retire_reason: metadata.retire_reason,
    },
    retired,
  }
}

function validateDuplicateIds(
  collection: { active: RuleRecord[]; retired: RuleRecord[] },
  errors: string[],
): void {
  const seen = new Map<string, string>()

  for (const rule of [...collection.active, ...collection.retired]) {
    const previousPath = seen.get(rule.id)

    if (previousPath) {
      errors.push(
        `duplicate GRL ID ${rule.id}: ${previousPath} and ${rule.path}`,
      )
      continue
    }

    seen.set(rule.id, rule.path)
  }
}

function validateIndexReferences(
  indexIds: Set<string>,
  collection: { active: RuleRecord[]; retired: RuleRecord[] },
  errors: string[],
): void {
  const activeIds = new Set(collection.active.map(rule => rule.id))
  const retiredIds = new Set(collection.retired.map(rule => rule.id))

  for (const id of indexIds) {
    if (retiredIds.has(id)) {
      errors.push(`index.md must not reference retired ${id}`)
    } else if (!activeIds.has(id)) {
      errors.push(`index.md references unknown ${id}`)
    }
  }
}

function validateBaseRule(
  root: string,
  rule: RuleRecord,
  errors: string[],
): void {
  const metadata = rule.metadata

  if (metadata.number !== rule.id) {
    errors.push(`${rule.path}: number must match filename ${rule.id}`)
  }

  if (!isNonEmptyString(metadata.short)) {
    errors.push(`${rule.path}: short must be a non-empty string`)
  }

  if (!isValidEnforcement(metadata.enforcement)) {
    errors.push(
      `${rule.path}: enforcement must include review boolean and lint string array`,
    )
  }

  if (metadata.references !== undefined) {
    if (!Array.isArray(metadata.references)) {
      errors.push(`${rule.path}: references must be an array when present`)
    } else {
      for (const reference of metadata.references) {
        validateReference(root, rule, reference, errors)
      }
    }
  }

  if (
    metadata.skip_index_reason !== undefined &&
    !isNonEmptyString(metadata.skip_index_reason)
  ) {
    errors.push(
      `${rule.path}: skip_index_reason must be a non-empty string when present`,
    )
  }

  if (
    metadata.lint_assist_reason !== undefined &&
    !isNonEmptyString(metadata.lint_assist_reason)
  ) {
    errors.push(
      `${rule.path}: lint_assist_reason must be a non-empty string when present`,
    )
  }
}

function validateActiveRule(
  rule: RuleRecord,
  indexIds: Set<string>,
  errors: string[],
): void {
  if (!isValidEnforcement(rule.metadata.enforcement)) {
    return
  }

  const enforcement = rule.metadata.enforcement
  const hasLint = enforcement.lint.length > 0
  const inIndex = indexIds.has(rule.id)
  const hasSkipReason = rule.metadata.skip_index_reason !== undefined
  const hasLintAssistReason = rule.metadata.lint_assist_reason !== undefined

  if (!enforcement.review && !hasLint) {
    errors.push(
      `${rule.path}: active rule must have at least one enforcement mechanism`,
    )
  }

  if (enforcement.review) {
    if (!inIndex) {
      errors.push(`${rule.path}: review-enforced rules must appear in index.md`)
    }

    if (hasSkipReason) {
      errors.push(
        `${rule.path}: review-enforced rules must not use skip_index_reason`,
      )
    }

    if (hasLint && !hasLintAssistReason) {
      errors.push(
        `${rule.path}: lint-assisted review rules require lint_assist_reason`,
      )
    }

    if (!hasLint && hasLintAssistReason) {
      errors.push(
        `${rule.path}: pure review rules must not use lint_assist_reason`,
      )
    }

    return
  }

  if (hasLint && !hasSkipReason) {
    errors.push(`${rule.path}: pure lint rules require skip_index_reason`)
  }

  if (inIndex) {
    errors.push(`${rule.path}: pure lint rules must not appear in index.md`)
  }

  if (hasLintAssistReason) {
    errors.push(`${rule.path}: pure lint rules must not use lint_assist_reason`)
  }
}

function validateRetiredRule(
  rule: RuleRecord,
  indexIds: Set<string>,
  errors: string[],
): void {
  if (!isNonEmptyString(rule.metadata.retire_reason)) {
    errors.push(`${rule.path}: retired rules require retire_reason`)
  }

  if (indexIds.has(rule.id)) {
    errors.push(`${rule.path}: retired rules must not appear in index.md`)
  }
}

function validateReference(
  root: string,
  rule: RuleRecord,
  reference: unknown,
  errors: string[],
): void {
  if (!isNonEmptyString(reference)) {
    errors.push(`${rule.path}: references entries must be non-empty strings`)
    return
  }

  const parsedReference = parseReference(reference)

  if (!parsedReference) {
    errors.push(
      `${rule.path}: reference line range must use :N or :N-M with positive line numbers: ${reference}`,
    )
    return
  }

  if (
    parsedReference.path.startsWith('/') ||
    parsedReference.path.split(/[\\/]/).includes('..')
  ) {
    errors.push(
      `${rule.path}: reference must be a repo-root relative path that does not escape the repo: ${reference}`,
    )
    return
  }

  const absoluteRoot = resolve(root)
  const absoluteReference = resolve(absoluteRoot, parsedReference.path)

  if (!isWithinRoot(absoluteRoot, absoluteReference)) {
    errors.push(`${rule.path}: reference escapes repo: ${reference}`)
    return
  }

  if (!existsSync(absoluteReference)) {
    errors.push(`${rule.path}: reference does not exist: ${reference}`)
    return
  }

  if (parsedReference.lineRange) {
    validateReferenceLineRange(
      rule,
      reference,
      absoluteReference,
      parsedReference.lineRange,
      errors,
    )
  }
}

function parseReference(reference: string): ParsedReference | null {
  const lineRangeMatch = /^(?<path>.+):(?<start>\d+)(?:-(?<end>\d+))?$/.exec(
    reference,
  )

  if (!lineRangeMatch?.groups) {
    return { path: reference }
  }

  const start = Number(lineRangeMatch.groups.start)
  const end = Number(lineRangeMatch.groups.end ?? lineRangeMatch.groups.start)

  if (start < 1 || end < start) {
    return null
  }

  return {
    path: lineRangeMatch.groups.path,
    lineRange: { start, end },
  }
}

function validateReferenceLineRange(
  rule: RuleRecord,
  reference: string,
  absoluteReference: string,
  lineRange: { start: number; end: number },
  errors: string[],
): void {
  if (!statSync(absoluteReference).isFile()) {
    errors.push(
      `${rule.path}: reference line range target must be a file: ${reference}`,
    )
    return
  }

  const lineCount = readFile(absoluteReference).split('\n').length

  if (lineRange.end > lineCount) {
    errors.push(
      `${rule.path}: reference line range exceeds file length (${lineCount} lines): ${reference}`,
    )
  }
}

function renderRule(rule: RuleRecord, detail: boolean): string {
  if (!detail) {
    return `## ${rule.id}\n\n${rule.metadata.short}`
  }

  const parts = [`## ${rule.id}`, rule.metadata.short]
  const body = shiftMarkdownHeadings(rule.body.trim())

  if (body.length > 0) {
    parts.push(body)
  }

  if (rule.metadata.references && rule.metadata.references.length > 0) {
    parts.push(
      [
        'References:',
        ...rule.metadata.references.map(reference => `- ${reference}`),
      ].join('\n'),
    )
  }

  return parts.join('\n\n')
}

/**
 * Rendered rules nest one level below the `## GRL-n` heading, so body headings
 * shift one level deeper. Lines inside fenced code blocks are left untouched —
 * a `#` comment in a YAML or shell example is not a heading — and H6 stays H6
 * because seven hashes is not a heading at all.
 */
function shiftMarkdownHeadings(source: string): string {
  let openingFence: string | undefined

  return source
    .split('\n')
    .map(line => {
      const fence = fencePattern.exec(line)

      if (fence) {
        const marker = fence[1] as string
        const info = fence[2] as string

        if (openingFence === undefined) {
          // A backtick fence cannot carry backticks in its info string, so
          // such a line is inline code rather than the start of a block.
          if (marker.startsWith('`') && info.includes('`')) {
            return shiftHeadingLine(line)
          }

          openingFence = marker

          return line
        }

        if (
          marker[0] === openingFence[0] &&
          marker.length >= openingFence.length &&
          info.trim() === ''
        ) {
          openingFence = undefined
        }

        return line
      }

      return openingFence === undefined ? shiftHeadingLine(line) : line
    })
    .join('\n')
}

function shiftHeadingLine(line: string): string {
  const heading = /^(#{1,6})(?=\s|$)/.exec(line)

  if (!heading) {
    return line
  }

  return (heading[1] as string).length < 6 ? `#${line}` : line
}

function scanIndexIds(source: string): Set<string> {
  return new Set(source.match(ruleTokenPattern) ?? [])
}

function uniqueStrings(values: string[]): string[] {
  const seen = new Set<string>()
  const result: string[] = []

  for (const value of values) {
    if (!seen.has(value)) {
      seen.add(value)
      result.push(value)
    }
  }

  return result
}

function ruleNumber(id: string): number {
  return Number(id.slice(ruleIdPrefix.length))
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function isValidEnforcement(value: unknown): value is Enforcement {
  if (!isRecord(value)) {
    return false
  }

  return (
    typeof value.review === 'boolean' &&
    Array.isArray(value.lint) &&
    value.lint.every(isNonEmptyString)
  )
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0
}

function readFile(path: string): string {
  return readFileSync(path, 'utf8').replace(/\r\n/g, '\n')
}

function isWithinRoot(absoluteRoot: string, absolutePath: string): boolean {
  return (
    absolutePath === absoluteRoot ||
    absolutePath.startsWith(`${absoluteRoot}${sep}`)
  )
}

function repoPath(root: string, path: string): string {
  const absoluteRoot = resolve(root)
  const absolutePath = resolve(absoluteRoot, path)

  if (!isWithinRoot(absoluteRoot, absolutePath)) {
    throw new Error(`path escapes repo root: ${path}`)
  }

  return absolutePath
}

if ((import.meta as { main?: boolean }).main) {
  const result = await runGuardrails({ args: process.argv.slice(2) })

  process.stdout.write(result.stdout)
  process.stderr.write(result.stderr)
  process.exit(result.exitCode)
}
