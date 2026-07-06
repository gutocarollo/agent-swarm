import pathlib
import json
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def assert_contains_all(testcase: unittest.TestCase, text: str, values: tuple[str, ...], label: str) -> None:
    for value in values:
        testcase.assertIn(value, text, f"{label}: missing {value}")


def assert_payload_block(
    testcase: unittest.TestCase,
    text: str,
    marker: str,
    fields: tuple[str, ...],
    label: str,
) -> None:
    match = re.search(rf"{re.escape(marker)}:\n(?P<body>(?:- .+\n?)+)", text)
    testcase.assertIsNotNone(match, f"{label}: missing bullet payload under {marker}")
    assert_contains_all(testcase, match.group("body"), fields, f"{label}: {marker}")


README = "README.md"
COUNCIL = ".agents/skills/learnhouse-delivery-council/SKILL.md"
REVIEWER = ".codex/agents/learnhouse-adversarial-reviewer.toml"
ADVERSARIAL = ".agents/skills/adversarial-review/SKILL.md"
AGENTS = "AGENTS.md"
PLAN_DOC = "docs/PLANO-SWARM.md"
SCHEMAS = "schemas"
WITNESS = "verification/witness-fixes.json"


class AgentContractRegressionTest(unittest.TestCase):
    def test_readme_has_single_ordered_pipeline_with_real_loops(self):
        text = read(README)

        self.assertEqual(text.count("```mermaid"), 1)
        self.assertIn("PLAN -> PLAN_REVIEW -> EXECUTION -> EXECUTION_REVIEW", text)
        self.assertIn('G1{"1. Rodar PLAN?"}', text)
        self.assertIn('G2{"2. Rodar PLAN_REVIEW?"}', text)
        self.assertIn('G3{"3. Rodar EXECUTION?"}', text)
        self.assertNotIn('C{"Modo"}', text)
        self.assertNotIn('C{"Primeira etapa"}', text)

        self.assertIn('P3 -->|"REPLANEJAR<br/>i < PLAN_REVIEW_MAX"| P4', text)
        self.assertIn('P4["REPLAN-CONSUMED<br/>corrigir plano<br/>i = i + 1"]', text)
        self.assertIn("P4 --> P2", text)
        self.assertIn('P3 -->|"REPLANEJAR<br/>i = PLAN_REVIEW_MAX"| PEND', text)
        self.assertIn('PEND["PENDENTE:<br/>limite do plano atingido"]', text)

        self.assertIn('H -->|"CORRIGIR<br/>j < EXECUTION_REVIEW_MAX"| I', text)
        self.assertIn('I["FIX-CONSUMED<br/>corrigir gap REAL<br/>BLOQUEANTE/ALTA<br/>j = j + 1"]', text)
        self.assertIn("I --> F", text)
        self.assertIn('H -->|"CORRIGIR<br/>j = EXECUTION_REVIEW_MAX"| EPEND', text)
        self.assertIn('EPEND["PENDENTE:<br/>limite da execucao atingido"]', text)

    def test_plan_loop_requires_request_and_consumption_handoff(self):
        for path in (README, COUNCIL, REVIEWER, ADVERSARIAL, AGENTS):
            text = read(path)
            self.assertIn("REPLAN-REQUEST", text, path)

        for path in (README, COUNCIL, ADVERSARIAL, AGENTS):
            text = read(path)
            self.assertIn("REPLAN-CONSUMED", text, path)

        council = read(COUNCIL)
        reviewer = read(REVIEWER)
        self.assertIn("o Council deve replanejar", council)
        self.assertIn("Sem `REPLAN-REQUEST`", council)
        self.assertIn("REPLAN-REQUEST block is mandatory", reviewer)
        self.assertIn("reviewer does not perform the replan", reviewer)
        for path in (README, COUNCIL, REVIEWER, ADVERSARIAL):
            assert_payload_block(
                self,
                read(path),
                "REPLAN-REQUEST",
                ("gap:", "evidencia:", "alteracao-obrigatoria:"),
                f"{path} REPLAN-REQUEST payload",
            )
        for path in (README, COUNCIL):
            assert_payload_block(
                self,
                read(path),
                "REPLAN-CONSUMED",
                ("source-review-round:", "gaps-incorporados:", "plano-alterado-em:", "decisao-atualizada:"),
                f"{path} REPLAN-CONSUMED payload",
            )

    def test_execution_loop_requires_request_and_consumption_handoff(self):
        for path in (README, COUNCIL, REVIEWER, ADVERSARIAL, AGENTS):
            text = read(path)
            self.assertIn("FIX-REQUEST", text, path)

        for path in (README, COUNCIL, ADVERSARIAL, AGENTS):
            text = read(path)
            self.assertIn("FIX-CONSUMED", text, path)

        council = read(COUNCIL)
        reviewer = read(REVIEWER)
        self.assertIn("O reviewer nao corrige", council)
        self.assertIn("Sem `FIX-REQUEST`", council)
        self.assertIn("FIX-REQUEST block is mandatory", reviewer)
        self.assertIn("The reviewer does not fix", reviewer)
        for path in (README, COUNCIL, REVIEWER, ADVERSARIAL):
            assert_payload_block(
                self,
                read(path),
                "FIX-REQUEST",
                ("gap:", "evidencia:", "alteracao-obrigatoria:"),
                f"{path} FIX-REQUEST payload",
            )
        for path in (README, COUNCIL):
            assert_payload_block(
                self,
                read(path),
                "FIX-CONSUMED",
                ("source-review-round:", "gaps-corrigidos:", "arquivos-alterados:", "validacao-rodada:"),
                f"{path} FIX-CONSUMED payload",
            )

    def test_final_negative_statuses_block_success_claims(self):
        readme = read(README)
        council = read(COUNCIL)
        reviewer = read(REVIEWER)

        self.assertIn("PLAN-ADVERSARIAL-LOOP: 2/2, status: PENDENTE", readme)
        self.assertIn("execucao nao comeca", readme)
        self.assertIn("execucao NAO pode comecar", council)
        self.assertIn("must not proceed to execution", reviewer)

        self.assertIn("ADVERSARIAL-LOOP: 3/3, status: PENDENTE", readme)
        self.assertIn("nao declare `ADVERSARIAL-VERIFICATION: SATISFEITO`", council)
        self.assertIn("must not declare SATISFEITO", reviewer)

    def test_required_sentinels_exist_once_per_loop_family(self):
        council = read(COUNCIL)
        reviewer = read(REVIEWER)
        adversarial = read(ADVERSARIAL)

        for text in (council, reviewer, adversarial):
            self.assertIn("PLAN-ADVERSARIAL-VERIFICATION: SATISFEITO | REPLANEJAR | BLOQUEADO", text)
            self.assertIn("ADVERSARIAL-VERIFICATION: SATISFEITO | CORRIGIR | BLOQUEADO", text)

        self.assertRegex(council, re.compile(r"PLAN-ADVERSARIAL-LOOP: <rodadas>/2"))
        self.assertRegex(council, re.compile(r"ADVERSARIAL-LOOP: <rodadas>/3"))

    def test_payload_assertion_is_scoped_to_marker_block(self):
        text = """
gap: elsewhere
evidencia: elsewhere
alteracao-obrigatoria: elsewhere
REPLAN-REQUEST:
- outro-campo: sem payload correto
"""
        with self.assertRaises(AssertionError):
            assert_payload_block(
                self,
                text,
                "REPLAN-REQUEST",
                ("gap:", "evidencia:", "alteracao-obrigatoria:"),
                "synthetic scoped payload",
            )

    def test_config_and_metadata_parse(self):
        tomllib.loads(read(".codex/config.toml"))
        for path in (ROOT / ".codex/agents").glob("*.toml"):
            tomllib.loads(path.read_text(encoding="utf-8"))

        metadata = read(".agents/skills/learnhouse-delivery-council/agents/openai.yaml")
        self.assertIn("interface:", metadata)
        self.assertIn("display_name:", metadata)
        self.assertIn("short_description:", metadata)
        self.assertIn("default_prompt:", metadata)

    def test_json_schemas_parse_and_enforce_conditional_payloads(self):
        plan_schema = json.loads(read("schemas/plan-review-result.schema.json"))
        execution_schema = json.loads(read("schemas/execution-review-result.schema.json"))
        ledger_schema = json.loads(read("schemas/ledger-event.schema.json"))

        self.assertEqual(plan_schema["properties"]["plan_adversarial_verification"]["enum"], ["SATISFEITO", "REPLANEJAR", "BLOQUEADO"])
        self.assertEqual(execution_schema["properties"]["adversarial_verification"]["enum"], ["SATISFEITO", "CORRIGIR", "BLOQUEADO"])
        self.assertIn("then", json.dumps(plan_schema))
        self.assertIn("replan_request", json.dumps(plan_schema))
        self.assertIn("then", json.dumps(execution_schema))
        self.assertIn("fix_request", json.dumps(execution_schema))
        self.assertEqual(ledger_schema["properties"]["event"]["enum"], ["review", "replan-request", "replan-consumed", "fix-request", "fix-consumed", "validation", "final"])

    def test_structured_schema_mirror_does_not_replace_markdown_sentinels(self):
        adversarial = read(ADVERSARIAL)
        reviewer = read(REVIEWER)
        for text in (adversarial, reviewer):
            self.assertIn("schemas/plan-review-result.schema.json", text)
            self.assertIn("schemas/execution-review-result.schema.json", text)
        self.assertIn("nao substitui os\nsentinels Markdown", adversarial)
        self.assertIn("Markdown sentinels remain mandatory", reviewer)

    def test_historical_plan_doc_is_marked_non_canonical(self):
        text = read(PLAN_DOC)
        self.assertIn("Documento historico", text)
        self.assertIn("Nao use como contrato operacional atual", text)
        self.assertIn("README.md", text)
        self.assertIn("learnhouse-delivery-council/SKILL.md", text)
        for sentinel in ("REPLAN-REQUEST", "REPLAN-CONSUMED", "FIX-REQUEST", "FIX-CONSUMED"):
            self.assertIn(sentinel, text)
        self.assertNotIn("execute quando o review ficar SATISFEITO", text)
        self.assertNotIn("corrija em sequência", text)

    def test_self_contained_validators_pass(self):
        for script in ("scripts/validate_skills.py", "scripts/verify_witness.py"):
            result = subprocess.run(
                ["python3", script],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_witness_markers_target_real_contract_files(self):
        witness = json.loads(read(WITNESS))
        self.assertEqual(witness["schema"], "agent-swarm-witness/v1")
        ids = [item["id"] for item in witness["fixes"]]
        self.assertEqual(len(ids), len(set(ids)))
        for fix in witness["fixes"]:
            text = read(fix["file"])
            self.assertIn(fix["marker"], text, fix["id"])

    def test_witness_fails_when_marker_is_missing(self):
        bad_witness = {
            "schema": "agent-swarm-witness/v1",
            "fixes": [
                {
                    "id": "BAD",
                    "desc": "missing marker must fail",
                    "file": "README.md",
                    "marker": "THIS_MARKER_SHOULD_NOT_EXIST_IN_AGENT_SWARM",
                }
            ],
        }
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json") as handle:
            json.dump(bad_witness, handle)
            handle.flush()
            result = subprocess.run(
                ["python3", "scripts/verify_witness.py", "--witness", handle.name],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("marker missing", result.stdout)

    def test_contract_validation_is_local_not_github_actions(self):
        workflows = ROOT / ".github" / "workflows"
        workflow_files = []
        if workflows.exists():
            workflow_files = list(workflows.glob("*.yml")) + list(workflows.glob("*.yaml"))
        self.assertEqual(workflow_files, [])
        readme = read(README)
        agents = read(AGENTS)
        self.assertIn("Nao ha GitHub Actions neste pacote", readme)
        self.assertIn("Nao adicione GitHub Actions", agents)
        self.assertIn("python3 scripts/validate_contract.py", readme)
        self.assertIn("python3 scripts/validate_contract.py", agents)

    def test_prompt_generator_validates_args(self):
        result = subprocess.run(
            ["python3", "scripts/render_prompt.py", "--start-at", "PLAN_REVIEW", "--task", "Executar plano"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--plan-source is required", result.stdout)

        result = subprocess.run(
            [
                "python3",
                "scripts/render_prompt.py",
                "--start-at",
                "EXECUTION",
                "--task",
                "Corrigir auth",
                "--execution-review-max",
                "3",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("START_AT=EXECUTION", result.stdout)
        self.assertIn("EXECUTION_REVIEW_MAX=3", result.stdout)

    def test_ledger_records_loop_events_as_jsonl(self):
        run_id = "unittest-ledger"
        run_dir = ROOT / ".agent-swarm" / "runs" / run_id
        shutil.rmtree(run_dir, ignore_errors=True)
        try:
            result = subprocess.run(
                [
                    "python3",
                    "scripts/agent_swarm_ledger.py",
                    "append",
                    "--run-id",
                    run_id,
                    "--loop",
                    "execution",
                    "--round",
                    "1",
                    "--event",
                    "fix-request",
                    "--status",
                    "CORRIGIR",
                    "--payload-json",
                    '{"gap":"g","evidencia":"e","alteracao_obrigatoria":"a"}',
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            ledger = run_dir / "loop.jsonl"
            entry = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(entry["loop"], "execution")
            self.assertEqual(entry["event"], "fix-request")
            self.assertEqual(entry["payload"]["gap"], "g")

            summary = subprocess.run(
                ["python3", "scripts/agent_swarm_ledger.py", "summary", "--run-id", run_id],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(summary.returncode, 0, summary.stdout)
            self.assertIn('"execution:fix-request": 1', summary.stdout)
        finally:
            shutil.rmtree(run_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
