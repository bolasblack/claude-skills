import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import {
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  unlinkSync,
  writeFileSync,
} from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import test, { after } from 'node:test'
import { fileURLToPath } from 'node:url'

import { runGuardrails } from './guardrails'

const temporaryDirectories: string[] = []

function createTempDir(prefix: string): string {
  const dir = mkdtempSync(join(tmpdir(), prefix))

  temporaryDirectories.push(dir)

  return dir
}

after(() => {
  for (const dir of temporaryDirectories.splice(0)) {
    rmSync(dir, { recursive: true, force: true })
  }
})

function createFixture(
  root: string = createTempDir('guardrails-validate-'),
): string {
  mkdirSync(join(root, '.agents/guardrails/rules'), { recursive: true })
  mkdirSync(join(root, '.agents/guardrails/retired-rules'), { recursive: true })
  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1\n',
  )
  writeRuleFile(root, 'rules/GRL-1.md', [
    'number: GRL-1',
    'short: Keep the hot-path rule visible.',
    'enforcement:',
    '  review: true',
    '  lint: []',
  ])

  return root
}

const changedGrl1 = [
  'number: GRL-1',
  'short: Keep the changed hot-path rule visible.',
  'enforcement:',
  '  review: true',
  '  lint: []',
]

function writeRuleFile(
  root: string,
  relativePath: string,
  frontmatter: string[],
  body: string[] = [],
): void {
  writeFileSync(
    join(root, '.agents/guardrails', relativePath),
    ['---', ...frontmatter, '---', '', ...body].join('\n'),
  )
}

/**
 * Structure-only view of review-metadata output: section title -> listed files.
 * Deliberately ignores instruction body prose so documentation rewording in
 * references/review-metadata-instructions/ cannot break these tests.
 */
function parseInstructionSections(stdout: string): Map<string, string[]> {
  const sections = new Map<string, string[]>()
  let title: string | undefined
  let inFiles = false

  for (const line of stdout.split('\n')) {
    if (line.startsWith('## ')) {
      title = line.slice(3)
      sections.set(title, [])
      inFiles = false
      continue
    }

    if (line === 'Files:') {
      inFiles = true
      continue
    }

    if (inFiles && line.startsWith('- ') && title !== undefined) {
      sections.get(title)?.push(line.slice(2))
      continue
    }

    if (inFiles && line === '') {
      inFiles = false
    }
  }

  return sections
}

function commitFixture(root: string): void {
  runGit(root, ['init'])
  commitAll(root, 'Initial guardrail fixture')
}

function commitAll(root: string, message: string): void {
  runGit(root, ['add', '-A'])
  runGit(root, [
    '-c',
    'user.name=Guardrail Test',
    '-c',
    'user.email=guardrail@example.test',
    'commit',
    '-m',
    message,
  ])
}

test('validate accepts a minimal rendered guardrail fixture', async () => {
  const root = createFixture()

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 0)
  assert.match(result.stdout, /Guardrail validation OK/)
  assert.equal(result.stderr, '')
})

test('validate ignores unrelated files that sit beside the router', async () => {
  const root = createFixture()

  mkdirSync(join(root, '.agents/tooling'), { recursive: true })
  writeFileSync(join(root, '.agents/guardrails/notes.json'), '{}\n')
  writeFileSync(
    join(root, '.agents/guardrails/overview.md'),
    '- Prose that mentions GRL-99 without being the router.\n',
  )
  writeFileSync(join(root, '.agents/tooling/report.py'), '# unrelated helper\n')

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(result.stdout, 'Guardrail validation OK.\n')
  assert.equal(result.stderr, '')
})

test('validate rejects a stray non-GRL Markdown file inside the rules directory', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/rules/README.md'),
    '- Notes about the rules directory.\n',
  )

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- rule file name must match GRL-<number>\.md: \.agents\/guardrails\/rules\/README\.md/,
  )
})

test('validate ignores directory entries inside the rules directory', async () => {
  const root = createFixture()

  mkdirSync(join(root, '.agents/guardrails/rules/drafts'), { recursive: true })

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(result.stdout, 'Guardrail validation OK.\n')
})

test('validate accepts lint-assisted review rules only when indexed with lint_assist_reason', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-2\n',
  )
  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Lint-assisted review rules stay visible for residual review judgment.',
    'enforcement:',
    '  review: true',
    '  lint:',
    '    - lint/no-cross-module-import',
    'lint_assist_reason: lint/no-cross-module-import catches the mechanical pattern; review still owns semantic fit.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 0)
  assert.match(result.stdout, /Guardrail validation OK/)
  assert.equal(result.stderr, '')
})

test('validate rejects lint-assisted review rules omitted from the index', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Lint-assisted review rules must remain indexed.',
    'enforcement:',
    '  review: true',
    '  lint:',
    '    - lint/no-cross-module-import',
    'lint_assist_reason: lint/no-cross-module-import catches the mechanical pattern; review still owns semantic fit.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(result.stderr, /review-enforced rules must appear in index.md/)
})

test('validate requires lint_assist_reason on lint-assisted review rules', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-2\n',
  )
  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Lint-assisted review rules explain residual review ownership.',
    'enforcement:',
    '  review: true',
    '  lint:',
    '    - lint/no-cross-module-import',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: lint-assisted review rules require lint_assist_reason/,
  )
})

test('validate rejects lint_assist_reason on pure review rules', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-2\n',
  )
  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Pure review rules have no lint-assisted reason.',
    'enforcement:',
    '  review: true',
    '  lint: []',
    'lint_assist_reason: No lint exists for this pure review rule.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: pure review rules must not use lint_assist_reason/,
  )
})

test('validate rejects lint_assist_reason on pure lint rules', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Pure lint rules stay out of review metadata.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
    'lint_assist_reason: Review owns nothing for this pure lint rule.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: pure lint rules must not use lint_assist_reason/,
  )
})

test('validate rejects an active rule with no enforcement mechanism', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Rules must declare at least one enforcement mechanism.',
    'enforcement:',
    '  review: false',
    '  lint: []',
    'skip_index_reason: No enforcement exists.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: active rule must have at least one enforcement mechanism/,
  )
})

test('validate rejects pure lint rules listed in the index', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-2\n',
  )
  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Indexed pure lint rules are invalid.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: pure lint rules must not appear in index\.md/,
  )
})

test('validate requires skip_index_reason on pure lint rules', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Pure lint rules document why they skip the router.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: pure lint rules require skip_index_reason/,
  )
})

test('render --detail emits the short, the body, and the references', async () => {
  const root = createFixture()

  writeRuleFile(
    root,
    'rules/GRL-2.md',
    [
      'number: GRL-2',
      'short: Mechanical rules can skip the hot-path index.',
      'enforcement:',
      '  review: false',
      '  lint:',
      '    - lint/no-test-import-in-runtime',
      'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
      'references:',
      '  - .agents/guardrails/index.md:1-2',
    ],
    ['# Detail', '', 'Longer detail.', ''],
  )

  const result = await runGuardrails({
    args: ['render', '--detail', 'GRL-2'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(
    result.stdout,
    [
      '# Guardrails',
      '',
      '## GRL-2',
      '',
      'Mechanical rules can skip the hot-path index.',
      '',
      '## Detail',
      '',
      'Longer detail.',
      '',
      'References:',
      '- .agents/guardrails/index.md:1-2',
      '',
    ].join('\n'),
  )
})

test('render --detail leaves comment lines inside fenced code blocks alone', async () => {
  const root = createFixture()

  writeRuleFile(
    root,
    'rules/GRL-2.md',
    [
      'number: GRL-2',
      'short: Pin third-party actions to a commit SHA.',
      'enforcement:',
      '  review: false',
      '  lint:',
      '    - lint/pin-action-sha',
      'skip_index_reason: Covered by lint/pin-action-sha diagnostics.',
    ],
    [
      '# Detail',
      '',
      '```yaml',
      '# pin to a commit SHA',
      'uses: actions/checkout@abc123',
      '```',
      '',
      '~~~sh',
      '# rebuild the lockfile',
      '~~~',
      '',
      '# After',
      '',
    ],
  )

  const result = await runGuardrails({
    args: ['render', '--detail', 'GRL-2'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(
    result.stdout,
    [
      '# Guardrails',
      '',
      '## GRL-2',
      '',
      'Pin third-party actions to a commit SHA.',
      '',
      '## Detail',
      '',
      '```yaml',
      '# pin to a commit SHA',
      'uses: actions/checkout@abc123',
      '```',
      '',
      '~~~sh',
      '# rebuild the lockfile',
      '~~~',
      '',
      '## After',
      '',
    ].join('\n'),
  )
})

test('render --detail keeps a level-six body heading at level six', async () => {
  const root = createFixture()

  writeRuleFile(
    root,
    'rules/GRL-2.md',
    [
      'number: GRL-2',
      'short: Deeply nested detail stays valid Markdown.',
      'enforcement:',
      '  review: false',
      '  lint:',
      '    - lint/no-deep-heading',
      'skip_index_reason: Covered by lint/no-deep-heading diagnostics.',
    ],
    ['##### Five', '', '###### Six', ''],
  )

  const result = await runGuardrails({
    args: ['render', '--detail', 'GRL-2'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(
    result.stdout,
    [
      '# Guardrails',
      '',
      '## GRL-2',
      '',
      'Deeply nested detail stays valid Markdown.',
      '',
      '###### Five',
      '',
      '###### Six',
      '',
    ].join('\n'),
  )
})

test('next-id returns one past the highest active or retired GRL number', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: The second rule stays visible.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
  ])
  writeRuleFile(root, 'retired-rules/GRL-9.md', [
    'number: GRL-9',
    'short: Retired numbers are never reused.',
    'enforcement:',
    '  review: true',
    '  lint: []',
    'retire_reason: Replaced by GRL-1.',
  ])

  const result = await runGuardrails({ args: ['next-id'], cwd: root })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(result.stdout, 'GRL-10\n')
})

test('validate rejects invalid reference line ranges', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Invalid line ranges fail validation.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
    'references:',
    '  - .agents/guardrails/index.md:3-2',
    '  - .agents/guardrails/index.md:99',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(result.stderr, /reference line range must use :N or :N-M/)
  assert.match(result.stderr, /reference line range exceeds file length/)
})

test('validate reports a missing router index file', async () => {
  const root = createFixture()

  unlinkSync(join(root, '.agents/guardrails/index.md'))

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- missing required file: \.agents\/guardrails\/index\.md/,
  )
})

test('validate reports a missing rules directory', async () => {
  const root = createFixture()

  rmSync(join(root, '.agents/guardrails/rules'), { recursive: true })

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- missing required directory: \.agents\/guardrails\/rules/,
  )
})

test('validate rejects rule files without YAML frontmatter', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/rules/GRL-2.md'),
    'number: GRL-2\nshort: No fence at all.\n',
  )

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: missing YAML frontmatter/,
  )
})

test('validate rejects rule files with unterminated YAML frontmatter', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/rules/GRL-2.md'),
    '---\nnumber: GRL-2\nshort: The fence never closes.\n',
  )

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: unterminated YAML frontmatter/,
  )
})

test('validate rejects rule frontmatter that is not a mapping', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/rules/GRL-2.md'),
    '---\n- GRL-2\n---\n\nBody.\n',
  )

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: frontmatter must be a mapping/,
  )
})

test('validate rejects a GRL number reused across active and retired rules', async () => {
  const root = createFixture()

  writeRuleFile(root, 'retired-rules/GRL-1.md', [
    'number: GRL-1',
    'short: The same number was retired without deleting the active file.',
    'enforcement:',
    '  review: true',
    '  lint: []',
    'retire_reason: Superseded by lint coverage.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- duplicate GRL ID GRL-1: \.agents\/guardrails\/rules\/GRL-1\.md and \.agents\/guardrails\/retired-rules\/GRL-1\.md/,
  )
})

test('validate reports every duplicate GRL ID, not just the first', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-2\n',
  )
  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: The second active rule also collides with a retired file.',
    'enforcement:',
    '  review: true',
    '  lint: []',
  ])
  writeRuleFile(root, 'retired-rules/GRL-1.md', [
    'number: GRL-1',
    'short: The first number was retired without deleting the active file.',
    'enforcement:',
    '  review: true',
    '  lint: []',
    'retire_reason: Superseded by lint coverage.',
  ])
  writeRuleFile(root, 'retired-rules/GRL-2.md', [
    'number: GRL-2',
    'short: The second number was retired without deleting the active file.',
    'enforcement:',
    '  review: true',
    '  lint: []',
    'retire_reason: Superseded by lint coverage.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- duplicate GRL ID GRL-1: \.agents\/guardrails\/rules\/GRL-1\.md and \.agents\/guardrails\/retired-rules\/GRL-1\.md/,
  )
  assert.match(
    result.stderr,
    /- duplicate GRL ID GRL-2: \.agents\/guardrails\/rules\/GRL-2\.md and \.agents\/guardrails\/retired-rules\/GRL-2\.md/,
  )
})

test('validate rejects an index entry for an unknown GRL', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-42\n',
  )

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(result.stderr, /- index\.md references unknown GRL-42/)
})

test('validate rejects an index entry for a retired GRL', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-9\n',
  )
  writeRuleFile(root, 'retired-rules/GRL-9.md', [
    'number: GRL-9',
    'short: Retired rules stay out of the router.',
    'enforcement:',
    '  review: true',
    '  lint: []',
    'retire_reason: Replaced by GRL-1.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(result.stderr, /- index\.md must not reference retired GRL-9/)
})

test('validate rejects retired rules listed in the index', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-9\n',
  )
  writeRuleFile(root, 'retired-rules/GRL-9.md', [
    'number: GRL-9',
    'short: Retired rules stay out of the router.',
    'enforcement:',
    '  review: true',
    '  lint: []',
    'retire_reason: Replaced by GRL-1.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/retired-rules\/GRL-9\.md: retired rules must not appear in index\.md/,
  )
})

test('validate rejects retired rules without retire_reason', async () => {
  const root = createFixture()

  writeRuleFile(root, 'retired-rules/GRL-9.md', [
    'number: GRL-9',
    'short: Retired rules explain why they were retired.',
    'enforcement:',
    '  review: true',
    '  lint: []',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/retired-rules\/GRL-9\.md: retired rules require retire_reason/,
  )
})

test('validate rejects a number field that disagrees with the filename', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-3',
    'short: The number field must match the filename.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: number must match filename GRL-2/,
  )
})

test('validate rejects rules whose short is missing or empty', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
  ])
  writeRuleFile(root, 'rules/GRL-3.md', [
    'number: GRL-3',
    "short: '   '",
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: short must be a non-empty string/,
  )
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-3\.md: short must be a non-empty string/,
  )
})

test('validate rejects malformed enforcement blocks', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Enforcement must be a mapping of review and lint.',
    'enforcement: review-only',
  ])
  writeRuleFile(root, 'rules/GRL-3.md', [
    'number: GRL-3',
    'short: Lint entries must be non-empty strings.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - 7',
    'skip_index_reason: Covered by lint diagnostics.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: enforcement must include review boolean and lint string array/,
  )
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-3\.md: enforcement must include review boolean and lint string array/,
  )
})

test('validate rejects a references field that is not an array', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: References must be a list.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
    'references: .agents/guardrails/index.md',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: references must be an array when present/,
  )
})

test('validate rejects reference entries that are not non-empty strings', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Reference entries must be non-empty strings.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
    'references:',
    "  - ''",
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: references entries must be non-empty strings/,
  )
})

test('validate rejects references to files that do not exist', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: References must point at real files.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
    'references:',
    '  - docs/never-written.md',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: reference does not exist: docs\/never-written\.md/,
  )
})

test('validate rejects references that escape the repo root', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: References stay inside the repository.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
    'references:',
    '  - ../escape.md',
    '  - /etc/passwd',
    '  - .agents/../../escape.md',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)

  const escapingReferences = [
    '../escape.md',
    '/etc/passwd',
    '.agents/../../escape.md',
  ]

  for (const reference of escapingReferences) {
    assert.ok(
      result.stderr.includes(
        `- .agents/guardrails/rules/GRL-2.md: reference must be a repo-root relative path that does not escape the repo: ${reference}`,
      ),
      `missing escape diagnostic for ${reference}:\n${result.stderr}`,
    )
  }
})

test('validate rejects a line range on a reference target that is not a file', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Line ranges only make sense on files.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: Covered by lint/no-test-import-in-runtime diagnostics.',
    'references:',
    '  - .agents/guardrails/rules:1-2',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: reference line range target must be a file: \.agents\/guardrails\/rules:1-2/,
  )
})

test('validate rejects a skip_index_reason that is present but empty', async () => {
  const root = createFixture()

  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: An empty skip_index_reason explains nothing.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    "skip_index_reason: '   '",
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: skip_index_reason must be a non-empty string when present/,
  )
})

test('validate rejects a lint_assist_reason that is present but empty', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-2\n',
  )
  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: An empty lint_assist_reason explains nothing.',
    'enforcement:',
    '  review: true',
    '  lint:',
    '    - lint/no-cross-module-import',
    "lint_assist_reason: '   '",
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: lint_assist_reason must be a non-empty string when present/,
  )
})

test('validate rejects review-enforced rules that use skip_index_reason', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-2\n',
  )
  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Review-enforced rules belong in the router.',
    'enforcement:',
    '  review: true',
    '  lint: []',
    'skip_index_reason: Pretending the router can be skipped.',
  ])

  const result = await runGuardrails({ args: ['validate'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.match(
    result.stderr,
    /- \.agents\/guardrails\/rules\/GRL-2\.md: review-enforced rules must not use skip_index_reason/,
  )
})

test('review-metadata prints only relevant instruction sections with files', async () => {
  const root = createFixture()

  commitFixture(root)

  writeRuleFile(root, 'rules/GRL-1.md', [
    'number: GRL-1',
    'short: Keep the changed hot-path rule visible.',
    'enforcement:',
    '  review: true',
    '  lint: []',
  ])
  writeFileSync(join(root, 'README.md'), 'Unrelated change.\n')
  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: Pure lint rules document router absence.',
    'enforcement:',
    '  review: false',
    '  lint:',
    '    - lint/no-test-import-in-runtime',
    'skip_index_reason: lint/no-test-import-in-runtime fully covers this mechanical rule.',
  ])

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'HEAD'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0)
  assert.doesNotMatch(result.stdout, /Changed guardrail review inputs/)
  assert.doesNotMatch(result.stdout, /\.\.\. \d+ more/)
  assert.match(result.stdout, /^Reviewer instructions:\n\n/)

  const sections = parseInstructionSections(result.stdout)

  assert.deepEqual(
    [...sections.keys()],
    ['Rule text changed', 'Enforcement changed', 'skip_index_reason changed'],
  )
  assert.deepEqual(sections.get('Rule text changed'), [
    '.agents/guardrails/rules/GRL-1.md',
    '.agents/guardrails/rules/GRL-2.md',
  ])
  assert.deepEqual(sections.get('Enforcement changed'), [
    '.agents/guardrails/rules/GRL-2.md',
  ])
  assert.deepEqual(sections.get('skip_index_reason changed'), [
    '.agents/guardrails/rules/GRL-2.md',
  ])
  assert.equal(result.stderr, '')
})

test('review-metadata reports router and retired rule guidance', async () => {
  const root = createFixture()

  writeRuleFile(root, 'retired-rules/GRL-9.md', [
    'number: GRL-9',
    'short: Retired rules stay out of the router.',
    'enforcement:',
    '  review: true',
    '  lint: []',
    'retire_reason: Replaced by GRL-1.',
  ])
  commitFixture(root)

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-9\n',
  )
  writeRuleFile(root, 'retired-rules/GRL-9.md', [
    'number: GRL-9',
    'short: Retired rules stay out of the router.',
    'enforcement:',
    '  review: true',
    '  lint: []',
    'retire_reason: Fully replaced by GRL-1 and its lint coverage.',
  ])

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'HEAD'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0)
  assert.doesNotMatch(result.stdout, /Changed guardrail review inputs/)
  assert.doesNotMatch(result.stdout, /\.\.\. \d+ more/)

  const sections = parseInstructionSections(result.stdout)

  assert.deepEqual(
    [...sections.keys()],
    ['Router changed', 'retire_reason changed or retired file added'],
  )
  assert.deepEqual(sections.get('Router changed'), [
    '.agents/guardrails/index.md',
  ])
  assert.deepEqual(
    sections.get('retire_reason changed or retired file added'),
    ['.agents/guardrails/retired-rules/GRL-9.md'],
  )
  assert.equal(result.stderr, '')
})

test('review-metadata reports deleted active rule guidance', async () => {
  const root = createFixture()

  commitFixture(root)

  unlinkSync(join(root, '.agents/guardrails/rules/GRL-1.md'))

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'HEAD'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0)

  const sections = parseInstructionSections(result.stdout)

  assert.deepEqual([...sections.keys()], ['Active rule removed'])
  assert.deepEqual(sections.get('Active rule removed'), [
    '.agents/guardrails/rules/GRL-1.md',
  ])
  assert.equal(result.stderr, '')
})

test('review-metadata reports a renumbered active rule as a removal', async () => {
  const root = createFixture()

  commitFixture(root)
  runGit(root, ['branch', 'guardrail-base'])
  runGit(root, [
    'mv',
    '.agents/guardrails/rules/GRL-1.md',
    '.agents/guardrails/rules/GRL-7.md',
  ])
  writeRuleFile(root, 'rules/GRL-7.md', [
    'number: GRL-7',
    'short: Keep the hot-path rule visible.',
    'enforcement:',
    '  review: true',
    '  lint: []',
  ])
  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-7\n',
  )
  commitAll(root, 'Renumber GRL-1 to GRL-7')

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'guardrail-base'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0)
  assert.match(result.stdout, /## Active rule removed/)
  assert.match(
    result.stdout,
    /Files:\n- \.agents\/guardrails\/rules\/GRL-1\.md/,
  )
  assert.equal(result.stderr, '')
})

test('review-metadata treats a moved rule as retirement, not removal', async () => {
  const root = createFixture()

  commitFixture(root)
  runGit(root, ['branch', 'guardrail-base'])
  runGit(root, [
    'mv',
    '.agents/guardrails/rules/GRL-1.md',
    '.agents/guardrails/retired-rules/GRL-1.md',
  ])
  writeRuleFile(root, 'retired-rules/GRL-1.md', [
    'number: GRL-1',
    'short: Keep the hot-path rule visible.',
    'enforcement:',
    '  review: true',
    '  lint: []',
    'retire_reason: Superseded by lint coverage.',
  ])
  writeFileSync(join(root, '.agents/guardrails/index.md'), '# Guardrails\n')
  commitAll(root, 'Retire GRL-1')

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'guardrail-base'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0)
  assert.doesNotMatch(result.stdout, /## Active rule removed/)
  assert.match(result.stdout, /## retire_reason changed or retired file added/)
  assert.match(
    result.stdout,
    /Files:\n- \.agents\/guardrails\/retired-rules\/GRL-1\.md/,
  )
  assert.equal(result.stderr, '')
})

test('review-metadata reports parse issue guidance from the catalog', async () => {
  const root = createFixture()

  commitFixture(root)

  writeFileSync(
    join(root, '.agents/guardrails/rules/GRL-1.md'),
    'number: GRL-1\nshort: Missing frontmatter fence.\n',
  )

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'HEAD'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0)
  assert.match(
    result.stdout,
    /- could not parse working tree \.agents\/guardrails\/rules\/GRL-1\.md: missing YAML frontmatter/,
  )

  const sections = parseInstructionSections(result.stdout)

  assert.deepEqual([...sections.keys()], ['Active rule removed', 'Parse issue'])
  assert.deepEqual(sections.get('Parse issue'), [
    '.agents/guardrails/rules/GRL-1.md',
  ])
  assert.equal(result.stderr, '')
})

test('review-metadata lists every relevant file without vague truncation', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    `# Guardrails\n\n- GRL-1, ${Array.from({ length: 13 }, (_, index) => `GRL-${index + 2}`).join(', ')}\n`,
  )

  for (let index = 2; index <= 14; index += 1) {
    writeRuleFile(root, `rules/GRL-${index}.md`, [
      `number: GRL-${index}`,
      `short: Initial rule ${index} stays visible.`,
      'enforcement:',
      '  review: true',
      '  lint: []',
    ])
  }

  commitFixture(root)

  for (let index = 2; index <= 14; index += 1) {
    writeRuleFile(root, `rules/GRL-${index}.md`, [
      `number: GRL-${index}`,
      `short: Changed rule ${index} stays visible.`,
      'enforcement:',
      '  review: true',
      '  lint: []',
    ])
  }

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'HEAD'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0)
  assert.doesNotMatch(result.stdout, /\.\.\. \d+ more/)

  for (let index = 2; index <= 14; index += 1) {
    assert.match(
      result.stdout,
      new RegExp(`- \\.agents/guardrails/rules/GRL-${index}\\.md`),
    )
  }
})

test('validate resolves the repo root from a nested working directory', async () => {
  const root = createFixture()
  const nested = join(root, 'packages/app/src')

  mkdirSync(nested, { recursive: true })

  const result = await runGuardrails({ args: ['validate'], cwd: nested })

  assert.equal(result.exitCode, 0)
  assert.equal(result.stdout, 'Guardrail validation OK.\n')
  assert.equal(result.stderr, '')
})

test('review-metadata finds changes when run from a nested working directory', async () => {
  const root = createFixture()

  commitFixture(root)

  writeRuleFile(root, 'rules/GRL-1.md', [
    'number: GRL-1',
    'short: Keep the changed hot-path rule visible.',
    'enforcement:',
    '  review: true',
    '  lint: []',
  ])

  const nested = join(root, 'packages/app/src')

  mkdirSync(nested, { recursive: true })

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'HEAD'],
    cwd: nested,
  })

  assert.equal(result.exitCode, 0)
  assert.notEqual(
    result.stdout,
    'No changed GRL files or guardrail router changes.\n',
  )
  assert.match(result.stdout, /## Rule text changed/)
  assert.match(result.stdout, /- \.agents\/guardrails\/rules\/GRL-1\.md/)
})

test('review-metadata honors the --base=<ref> form', async () => {
  const root = createFixture()

  commitFixture(root)

  writeRuleFile(root, 'rules/GRL-1.md', [
    'number: GRL-1',
    'short: Keep the changed hot-path rule visible.',
    'enforcement:',
    '  review: true',
    '  lint: []',
  ])

  const result = await runGuardrails({
    args: ['review-metadata', '--base=HEAD'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0)
  assert.notEqual(
    result.stdout,
    'No changed GRL files or guardrail router changes.\n',
  )
  assert.match(result.stdout, /## Rule text changed/)
  assert.match(result.stdout, /- \.agents\/guardrails\/rules\/GRL-1\.md/)
})

test('review-metadata reports an unknown base ref as an actionable error', async () => {
  const root = createFixture()

  commitFixture(root)

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'refs/heads/does-not-exist'],
    cwd: root,
  })

  assert.equal(result.exitCode, 1)
  assert.ok(
    result.stderr.startsWith('Base ref not found: refs/heads/does-not-exist'),
    result.stderr,
  )
  assert.doesNotMatch(result.stderr, /usage: git/i)
  assert.doesNotMatch(result.stderr, /--no-index/)
})

test('review-metadata fails with a direct message when git resolves no repository', async () => {
  const root = createFixture()

  // A dangling `gitdir:` pointer makes `git rev-parse --show-toplevel` fail
  // regardless of whether an ancestor directory happens to be a repository, so
  // this test runs everywhere instead of silently skipping itself.
  writeFileSync(join(root, '.git'), 'gitdir: /guardrails-test-no-such-gitdir\n')
  assert.notEqual(
    spawnSync('git', ['rev-parse', '--show-toplevel'], {
      cwd: root,
      encoding: 'utf8',
    }).status,
    0,
  )

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'HEAD'],
    cwd: root,
  })

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    'review-metadata requires running inside a git repository.\n',
  )
})

test('--root overrides root resolution for validate', async () => {
  const root = createFixture()

  const result = await runGuardrails({
    args: ['validate', '--root', root],
    cwd: createTempDir('guardrails-cwd-'),
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(result.stdout, 'Guardrail validation OK.\n')
})

test('--root is stripped before render parses GRL IDs', async () => {
  const root = createFixture()

  const result = await runGuardrails({
    args: ['render', '--root', root, 'GRL-1'],
    cwd: createTempDir('guardrails-cwd-'),
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(
    result.stdout,
    [
      '# Guardrails',
      '',
      '## GRL-1',
      '',
      'Keep the hot-path rule visible.',
      '',
    ].join('\n'),
  )
})

test('--root=<dir> is accepted as an inline option', async () => {
  const root = createFixture()

  const result = await runGuardrails({
    args: ['validate', `--root=${root}`],
    cwd: createTempDir('guardrails-cwd-'),
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(result.stdout, 'Guardrail validation OK.\n')
})

test('--root without a value is an actionable error', async () => {
  const result = await runGuardrails({
    args: ['validate', '--root'],
    cwd: createTempDir('guardrails-cwd-'),
  })

  assert.equal(result.exitCode, 1)
  assert.equal(result.stderr, '--root requires a directory\n')
})

test('render reports an unknown GRL ID', async () => {
  const root = createFixture()

  const result = await runGuardrails({
    args: ['render', '--root', root, 'GRL-2'],
    cwd: createTempDir('guardrails-cwd-'),
  })

  assert.equal(result.exitCode, 1)
  assert.equal(result.stderr, 'Unknown GRL ID: GRL-2\n')
})

test('an unrecognized command is an actionable error', async () => {
  const root = createFixture()

  const result = await runGuardrails({ args: ['lint'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.equal(result.stderr, 'Unknown command: lint\n')
})

test('a missing command is an actionable error', async () => {
  const root = createFixture()

  const result = await runGuardrails({ args: [], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.equal(result.stderr, 'Unknown command: (missing)\n')
})

test('review-metadata --base without a value is an actionable error', async () => {
  const root = createFixture()

  commitFixture(root)

  const result = await runGuardrails({
    args: ['review-metadata', '--base'],
    cwd: root,
  })

  assert.equal(result.exitCode, 1)
  assert.equal(result.stderr, 'review-metadata --base requires a base ref\n')
})

test('render without --detail emits only the heading and short', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-2\n',
  )
  writeRuleFile(
    root,
    'rules/GRL-2.md',
    [
      'number: GRL-2',
      'short: Lint-assisted review rules stay visible.',
      'enforcement:',
      '  review: true',
      '  lint:',
      '    - lint/no-cross-module-import',
      'lint_assist_reason: The lint catches the mechanical pattern; review owns semantic fit.',
      'references:',
      '  - .agents/guardrails/index.md:1-2',
    ],
    ['# Detail', '', 'Longer detail nobody asked for.', ''],
  )

  const result = await runGuardrails({ args: ['render', 'GRL-2'], cwd: root })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(
    result.stdout,
    [
      '# Guardrails',
      '',
      '## GRL-2',
      '',
      'Lint-assisted review rules stay visible.',
      '',
    ].join('\n'),
  )
})

test('render keeps the requested ID order and emits each rule once', async () => {
  const root = createFixture()

  writeFileSync(
    join(root, '.agents/guardrails/index.md'),
    '# Guardrails\n\n- GRL-1, GRL-2\n',
  )
  writeRuleFile(root, 'rules/GRL-2.md', [
    'number: GRL-2',
    'short: The second rule stays visible.',
    'enforcement:',
    '  review: true',
    '  lint: []',
  ])

  const result = await runGuardrails({
    args: ['render', 'GRL-2', 'GRL-1', 'GRL-2'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(
    result.stdout,
    [
      '# Guardrails',
      '',
      '## GRL-2',
      '',
      'The second rule stays visible.',
      '',
      '## GRL-1',
      '',
      'Keep the hot-path rule visible.',
      '',
    ].join('\n'),
  )
  assert.equal(result.stdout.match(/## GRL-2/g)?.length, 1)

  const reversed = await runGuardrails({
    args: ['render', 'GRL-1', 'GRL-2'],
    cwd: root,
  })

  assert.equal(reversed.exitCode, 0, reversed.stderr)
  assert.equal(
    reversed.stdout,
    [
      '# Guardrails',
      '',
      '## GRL-1',
      '',
      'Keep the hot-path rule visible.',
      '',
      '## GRL-2',
      '',
      'The second rule stays visible.',
      '',
    ].join('\n'),
  )
})

test('render refuses a retired GRL and reports its retire_reason', async () => {
  const root = createFixture()

  writeRuleFile(root, 'retired-rules/GRL-9.md', [
    'number: GRL-9',
    'short: Retired rules stay out of the router.',
    'enforcement:',
    '  review: true',
    '  lint: []',
    'retire_reason: Fully replaced by GRL-1 and its lint coverage.',
  ])

  const result = await runGuardrails({ args: ['render', 'GRL-9'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    'Cannot render retired GRL-9: Fully replaced by GRL-1 and its lint coverage.\n',
  )
})

test('render requires at least one explicit GRL ID', async () => {
  const root = createFixture()

  const result = await runGuardrails({ args: ['render'], cwd: root })

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    'render requires at least one explicit GRL ID\n',
  )
})

test('render accepts --detail in any argument position', async () => {
  const root = createFixture()

  writeRuleFile(
    root,
    'rules/GRL-1.md',
    [
      'number: GRL-1',
      'short: Keep the hot-path rule visible.',
      'enforcement:',
      '  review: true',
      '  lint: []',
    ],
    ['Longer detail.', ''],
  )

  const trailing = await runGuardrails({
    args: ['render', 'GRL-1', '--detail'],
    cwd: root,
  })

  assert.equal(trailing.exitCode, 0, trailing.stderr)
  assert.equal(
    trailing.stdout,
    [
      '# Guardrails',
      '',
      '## GRL-1',
      '',
      'Keep the hot-path rule visible.',
      '',
      'Longer detail.',
      '',
    ].join('\n'),
  )

  const leading = await runGuardrails({
    args: ['render', '--detail', 'GRL-1'],
    cwd: root,
  })

  assert.equal(leading.exitCode, 0, leading.stderr)
  assert.equal(leading.stdout, trailing.stdout)
})

test('render rejects non-GRL tokens other than --detail', async () => {
  const root = createFixture()

  const result = await runGuardrails({
    args: ['render', '--verbose', 'GRL-1'],
    cwd: root,
  })

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    'render accepts only explicit GRL IDs: --verbose\n',
  )
})

const instructionCatalogKeys = [
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
]

function createInstructionCatalog(
  options: {
    omit?: string[]
    extraFiles?: Record<string, string>
    extraDirs?: string[]
  } = {},
): string {
  const dir = createTempDir('guardrails-catalog-')
  const omitted = new Set(options.omit ?? [])

  for (const key of instructionCatalogKeys) {
    if (omitted.has(key)) {
      continue
    }

    writeFileSync(
      join(dir, `${key}.md`),
      `---\ntitle: Fixture ${key}\n---\n\n- Fixture guidance for ${key}.\n`,
    )
  }

  for (const [name, contents] of Object.entries(options.extraFiles ?? {})) {
    writeFileSync(join(dir, name), contents)
  }

  for (const name of options.extraDirs ?? []) {
    mkdirSync(join(dir, name), { recursive: true })
  }

  return dir
}

async function reviewMetadataWithCatalog(
  instructionsDir: string,
): Promise<Awaited<ReturnType<typeof runGuardrails>>> {
  const root = createFixture()

  commitFixture(root)
  writeRuleFile(root, 'rules/GRL-1.md', changedGrl1)

  return runGuardrails({
    args: ['review-metadata', '--base', 'HEAD'],
    cwd: root,
    instructionsDir,
  })
}

test('review-metadata fails closed when the instruction directory is missing', async () => {
  const missing = join(
    createTempDir('guardrails-catalog-'),
    'not-created',
  )

  const result = await reviewMetadataWithCatalog(missing)

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    `Missing review metadata instruction directory: ${missing}\n`,
  )
})

test('review-metadata fails closed when an expected instruction key is missing', async () => {
  const result = await reviewMetadataWithCatalog(
    createInstructionCatalog({ omit: ['rule-text', 'router'] }),
  )

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    'Missing review metadata instruction keys: router, rule-text\n',
  )
})

test('review-metadata fails closed on an unknown instruction key', async () => {
  const result = await reviewMetadataWithCatalog(
    createInstructionCatalog({
      extraFiles: {
        'bonus-guidance.md': '---\ntitle: Bonus\n---\n\n- Extra guidance.\n',
      },
    }),
  )

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    'Unknown review metadata instruction key: bonus-guidance\n',
  )
})

test('review-metadata fails closed on a non-Markdown instruction file', async () => {
  const result = await reviewMetadataWithCatalog(
    createInstructionCatalog({
      extraFiles: { 'notes.txt': 'Scratch notes.\n' },
    }),
  )

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    'Review metadata instruction file must be Markdown: notes.txt\n',
  )
})

test('review-metadata fails closed on a nested instruction directory entry', async () => {
  const result = await reviewMetadataWithCatalog(
    createInstructionCatalog({ extraDirs: ['archive'] }),
  )

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    'Unexpected review metadata instruction entry: archive\n',
  )
})

test('review-metadata fails closed on an instruction file without frontmatter', async () => {
  const instructionsDir = createInstructionCatalog({
    extraFiles: { 'rule-text.md': '- No frontmatter fence here.\n' },
  })

  const result = await reviewMetadataWithCatalog(instructionsDir)

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    `${join(instructionsDir, 'rule-text.md')}: missing YAML frontmatter\n`,
  )
})

test('review-metadata fails closed on an instruction file with an empty title', async () => {
  const instructionsDir = createInstructionCatalog({
    extraFiles: {
      'rule-text.md': '---\ntitle: "   "\n---\n\n- Guidance.\n',
    },
  })

  const result = await reviewMetadataWithCatalog(instructionsDir)

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    `${join(instructionsDir, 'rule-text.md')}: title must be a non-empty string\n`,
  )
})

test('review-metadata fails closed on an instruction file with an empty body', async () => {
  const instructionsDir = createInstructionCatalog({
    extraFiles: { 'rule-text.md': '---\ntitle: Rule text changed\n---\n' },
  })

  const result = await reviewMetadataWithCatalog(instructionsDir)

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    `${join(instructionsDir, 'rule-text.md')}: body must be non-empty\n`,
  )
})

test('the shipped instruction catalog defines every expected key with a non-empty title and body', () => {
  const shipped = join(
    dirname(fileURLToPath(import.meta.url)),
    '..',
    'references',
    'review-metadata-instructions',
  )

  assert.deepEqual(
    readdirSync(shipped).sort(),
    instructionCatalogKeys.map(key => `${key}.md`).sort(),
  )

  for (const entry of readdirSync(shipped).sort()) {
    const source = readFileSync(join(shipped, entry), 'utf8')
    const parsed = /^---\ntitle:(?<title>[^\n]*)\n---\n(?<body>[\s\S]*)$/.exec(
      source,
    )

    assert.ok(
      parsed?.groups,
      `${entry} must open with a title frontmatter block`,
    )
    assert.ok(
      (parsed?.groups?.title ?? '').trim().length > 0,
      `${entry} must declare a non-empty title`,
    )
    assert.ok(
      (parsed?.groups?.body ?? '').trim().length > 0,
      `${entry} must have a non-empty body`,
    )
  }
})

test('review-metadata reads instruction sections from the caller-supplied instructions directory', async () => {
  const root = createFixture()

  commitFixture(root)

  writeRuleFile(root, 'rules/GRL-1.md', [
    'number: GRL-1',
    'short: Keep the changed hot-path rule visible.',
    'enforcement:',
    '  review: true',
    '  lint: []',
  ])

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'HEAD'],
    cwd: root,
    instructionsDir: createInstructionCatalog(),
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.match(result.stdout, /## Fixture rule-text/)
  assert.match(result.stdout, /- Fixture guidance for rule-text\./)
  assert.doesNotMatch(result.stdout, /## Rule text changed/)
})

test('GUARDRAILS_ROOT from the caller-supplied env resolves the guardrail root', async () => {
  const root = createFixture()
  const unrelatedCwd = createTempDir('guardrails-cwd-')

  const result = await runGuardrails({
    args: ['validate'],
    cwd: unrelatedCwd,
    env: { GUARDRAILS_ROOT: root },
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(result.stdout, 'Guardrail validation OK.\n')
})

test('review-metadata uses GUARDRAILS_BASE when no --base is given', async () => {
  const root = createFixture()

  commitFixture(root)
  runGit(root, ['branch', 'guardrail-base'])
  writeRuleFile(root, 'rules/GRL-1.md', changedGrl1)
  commitAll(root, 'Change GRL-1')

  const result = await runGuardrails({
    args: ['review-metadata'],
    cwd: root,
    env: { GUARDRAILS_BASE: 'guardrail-base' },
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.match(result.stdout, /## Rule text changed/)
  assert.match(result.stdout, /Files:\n- \.agents\/guardrails\/rules\/GRL-1\.md/)
  assert.equal(result.stderr, '')
})

test('review-metadata falls back to origin/HEAD when no base is supplied', async () => {
  const root = createFixture()

  commitFixture(root)
  runGit(root, ['remote', 'add', 'origin', root])
  runGit(root, ['update-ref', 'refs/remotes/origin/trunk', 'HEAD'])
  runGit(root, [
    'symbolic-ref',
    'refs/remotes/origin/HEAD',
    'refs/remotes/origin/trunk',
  ])
  writeRuleFile(root, 'rules/GRL-1.md', changedGrl1)
  commitAll(root, 'Change GRL-1')

  const result = await runGuardrails({
    args: ['review-metadata'],
    cwd: root,
    env: {},
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.match(result.stdout, /## Rule text changed/)
  assert.match(result.stdout, /Files:\n- \.agents\/guardrails\/rules\/GRL-1\.md/)
  assert.equal(result.stderr, '')
})

test('review-metadata notes the HEAD fallback when origin/HEAD is unset', async () => {
  const root = createFixture()

  commitFixture(root)
  writeRuleFile(root, 'rules/GRL-1.md', changedGrl1)

  const result = await runGuardrails({
    args: ['review-metadata'],
    cwd: root,
    env: {},
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.match(result.stdout, /## Rule text changed/)
  assert.equal(
    result.stderr,
    'No --base given and origin/HEAD is not configured; comparing against HEAD.\n',
  )
})

test('review-metadata reports a clean tree when no guardrail files changed', async () => {
  const root = createFixture()

  commitFixture(root)

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'HEAD'],
    cwd: root,
  })

  assert.equal(result.exitCode, 0, result.stderr)
  assert.equal(
    result.stdout,
    'No changed GRL files or guardrail router changes.\n',
  )
  assert.equal(result.stderr, '')
})

test('review-metadata requires the guardrail root to be the git root', async () => {
  const outer = createTempDir('guardrails-outer-')
  const nested = join(outer, 'nested')

  mkdirSync(nested, { recursive: true })
  runGit(outer, ['init'])
  createFixture(nested)

  const result = await runGuardrails({
    args: ['review-metadata', '--base', 'HEAD'],
    cwd: nested,
  })

  assert.equal(result.exitCode, 1)
  assert.equal(
    result.stderr,
    `review-metadata requires the guardrails root to match the git repository root (guardrails root: ${nested}, git root: ${outer})\n`,
  )
})

function runGit(cwd: string, args: string[]): void {
  const result = spawnSync('git', args, { cwd, encoding: 'utf8' })

  assert.equal(result.status, 0, result.stderr)
}
