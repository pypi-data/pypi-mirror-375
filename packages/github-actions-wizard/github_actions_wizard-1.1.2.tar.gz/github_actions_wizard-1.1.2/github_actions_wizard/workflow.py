import os
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

yaml = YAML()


class Workflow:
    def __init__(self, name="CI Pipeline", run_name="CI Pipeline"):
        self.workflow = {"name": name, "run-name": run_name, "on": {}, "jobs": {}}
        self.file_name = "gha_workflow.yml"

    def has_job(self, job_id):
        return job_id in self.workflow["jobs"]

    def get_jobs(self):
        return self.workflow["jobs"].keys()

    def set_name(self, name, run_name=None):
        self.workflow["name"] = name
        if run_name:
            self.workflow["run-name"] = run_name
        return self

    def add_read_permission(self, job_id):
        if "permissions" not in self.workflow["jobs"][job_id]:
            self.workflow["jobs"][job_id]["permissions"] = {}

        self.workflow["jobs"][job_id]["permissions"]["contents"] = "read"

    def add_id_token_write_permission(self, job_id):
        if "permissions" not in self.workflow["jobs"][job_id]:
            self.workflow["jobs"][job_id]["permissions"] = {}

        self.workflow["jobs"][job_id]["permissions"]["id-token"] = "write"

    def add_trigger_push(self, branches):
        self._add_trigger("push", "branches", branches)

    def add_trigger_release(self, types=["created"]):
        self._add_trigger("release", "types", types)

    def add_job(self, job_id, **job):
        job["runs-on"] = job.get("runs-on", "ubuntu-latest")
        job["steps"] = []
        if "needs" in job and not isinstance(job["needs"], list):
            job["needs"] = [job["needs"]]
        job["permissions"] = job.get("permissions", {"contents": "read"})
        self.workflow["jobs"][job_id] = job

    def get_job_field(self, job_id, field):
        return self.workflow["jobs"][job_id].get(field)

    def set_job_field(self, job_id, field, value):
        self.workflow["jobs"][job_id][field] = value
        return self

    def remove_job_field(self, job_id, field):
        if field in self.workflow["jobs"][job_id]:
            del self.workflow["jobs"][job_id][field]

    def get_jobs_ids(self):
        return list(self.workflow["jobs"].keys())

    def add_upload_artifact_step(self, job_id, name="Upload Artifact", path="build"):
        step = {
            "name": name,
            "uses": "actions/upload-artifact@v4",
            "with": {"name": "build", "path": path},
        }
        self.add_job_step(job_id, **step)

    def add_download_artifact_step(self, job_id, name="Download Artifact", path="build"):
        step = {
            "name": name,
            "uses": "actions/download-artifact@v5",
            "with": {"name": "build", "path": path},
        }
        self.add_job_step(job_id, **step)

    def add_checkout_step(self, job_id):
        self.add_job_step(job_id, name="Checkout", uses="actions/checkout@v4")

    def replace_checkout_step_with_download_artifact(self, job_id, path="build"):
        steps = self.workflow["jobs"][job_id]["steps"]
        for i, step in enumerate(steps):
            if step.get("uses", "").startswith("actions/checkout@"):
                steps[i] = {
                    "name": "Download Artifact",
                    "uses": "actions/download-artifact@v5",
                    "with": {"name": "build", "path": path},
                }
                break
        return self

    def add_job_step(self, job_id, **step):
        self.workflow["jobs"][job_id]["steps"].append(step)

    def add_job_shell_step(self, job_id, cmds, **step):
        if isinstance(cmds, list):
            run_cmd = "\n".join(cmds)
        else:
            run_cmd = cmds

        step["run"] = LiteralScalarString(run_cmd)  # Always use LiteralScalarString for block style (|) in YAML
        self.add_job_step(job_id, **step)
        return self

    def add_cron_step(self, cron):
        self.workflow["on"]["schedule"] = [{"cron": cron}]
        return self

    def save(self):
        path = f".github/workflows/{self.file_name}"
        os.makedirs(os.path.dirname(path), exist_ok=True)

        is_new_file = not os.path.exists(path)
        comment = (
            "# Generated initially using github-actions-wizard (https://github.com/cmdr2/github-actions-wizard)\n\n"
        )
        with open(path, "w") as f:
            if is_new_file:
                f.write(comment)
            yaml.dump(self.workflow, f)
        return path

    def load(self):
        path = f".github/workflows/{self.file_name}"
        if not os.path.exists(path):
            return

        with open(path, "r") as f:
            self.workflow = yaml.load(f)
        return self

    def reorder_jobs(self, ordered_job_ids):
        ordered_jobs = {
            job_id: self.workflow["jobs"][job_id] for job_id in ordered_job_ids if job_id in self.workflow["jobs"]
        }
        self.workflow["jobs"] = ordered_jobs
        return self

    def _add_trigger(self, trigger_type, types_key, types):
        types = types if isinstance(types, list) else [types]

        self.workflow["on"][trigger_type] = self.workflow["on"].get(trigger_type, {})
        self.workflow["on"][trigger_type][types_key] = self.workflow["on"][trigger_type].get(types_key, [])

        for t in types:
            if t not in self.workflow["on"][trigger_type][types_key]:
                self.workflow["on"][trigger_type][types_key].append(t)
