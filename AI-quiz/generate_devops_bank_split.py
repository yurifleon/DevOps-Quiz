#!/usr/bin/env python3
"""
DevOps Quiz Bank Generator (200 questions) — split into files per category

Outputs:
- out_dir/
  - index.json                 # summary + list of category files
  - DevOps_Fundamentals.json
  - Version_Control.json
  - Linux.json
  - Networking.json
  - CI_CD.json
  - Containers.json
  - Kubernetes.json
  - Infrastructure_as_Code.json
  - Observability.json
  - Security.json
  - Cloud.json
  - Testing.json
  - Reliability.json
  - Automation.json
  - HTTP.json
  - Release.json
  ...

Each question schema:
{
  "id": int,                    # unique globally across all categories
  "category": str,
  "difficulty": "easy"|"medium"|"hard",
  "type": "mcq"|"true_false"|"short_answer",
  "question": str,
  "options": [str,...] | null,  # only for mcq
  "answer": str,                # stored as exact option text; TF as "true"/"false"
  "explanation": str,
  "tags": [str,...]
}

Notes:
- Answers are stored as text to allow safe shuffling of options in your quiz app.
- IDs are global, not per-category (easy to track progress across files).
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Tuple


@dataclass
class Question:
    id: int
    category: str
    difficulty: str
    type: str
    question: str
    options: Optional[List[str]]
    answer: str
    explanation: str
    tags: List[str]


def _mcq(category: str, difficulty: str, prompt: str, options: List[str], answer: str,
         explanation: str, tags: List[str]) -> Dict[str, Any]:
    if answer not in options:
        raise ValueError(f"MCQ answer must be one of the options. Got {answer!r}")
    return {
        "category": category,
        "difficulty": difficulty,
        "type": "mcq",
        "question": prompt,
        "options": options,
        "answer": answer,
        "explanation": explanation,
        "tags": tags,
    }


def _tf(category: str, difficulty: str, prompt: str, answer_bool: bool,
        explanation: str, tags: List[str]) -> Dict[str, Any]:
    return {
        "category": category,
        "difficulty": difficulty,
        "type": "true_false",
        "question": prompt,
        "options": None,
        "answer": "true" if answer_bool else "false",
        "explanation": explanation,
        "tags": tags,
    }


def _sa(category: str, difficulty: str, prompt: str, answer: str,
        explanation: str, tags: List[str]) -> Dict[str, Any]:
    return {
        "category": category,
        "difficulty": difficulty,
        "type": "short_answer",
        "question": prompt,
        "options": None,
        "answer": answer,
        "explanation": explanation,
        "tags": tags,
    }


def build_seed_templates() -> List[Dict[str, Any]]:
    T: List[Dict[str, Any]] = []

    # Core categories
    T += [
        _mcq("DevOps Fundamentals", "easy",
             "What is the primary goal of DevOps?",
             ["Improve collaboration between development and operations",
              "Eliminate testing",
              "Replace developers with automation",
              "Only reduce infrastructure cost"],
             "Improve collaboration between development and operations",
             "DevOps emphasizes culture + collaboration + automation across the SDLC.",
             ["devops", "culture"]),
        _tf("DevOps Fundamentals", "easy",
            "DevOps is only a set of tools, not a cultural practice.",
            False,
            "DevOps includes culture/process plus tools and automation.",
            ["devops", "culture"]),
        _sa("DevOps Fundamentals", "medium",
            "Name one common DevOps metric related to release performance (e.g., from DORA).",
            "lead time",
            "DORA metrics include lead time, deployment frequency, change failure rate, and MTTR.",
            ["devops", "metrics", "dora"]),

        _mcq("Version Control", "easy",
             "Which Git command creates a new local repository?",
             ["git init", "git start", "git clone --new", "git repo create"],
             "git init",
             "git init initializes a new Git repository in the current directory.",
             ["git", "vcs"]),
        _mcq("Version Control", "easy",
             "Which Git command stages changes for commit?",
             ["git add", "git push", "git commit", "git stage"],
             "git add",
             "git add stages changes in the index (staging area).",
             ["git", "vcs"]),
        _mcq("Version Control", "medium",
             "What does `git rebase` primarily do?",
             ["Moves or combines commits to a new base commit",
              "Deletes a remote branch",
              "Encrypts the repository history",
              "Creates a new repository"],
             "Moves or combines commits to a new base commit",
             "Rebasing rewrites commit history by replaying commits onto a new base.",
             ["git", "history"]),
        _tf("Version Control", "medium",
            "A fast-forward merge creates a merge commit.",
            False,
            "Fast-forward merges advance the branch pointer without a merge commit.",
            ["git", "merge"]),

        _mcq("Linux", "easy",
             "Which command displays current running processes in real-time?",
             ["top", "cat", "grep", "tar"],
             "top",
             "`top` shows real-time process information.",
             ["linux", "ops"]),
        _mcq("Linux", "medium",
             "What does `chmod 640 file` set?",
             ["Owner: read+write, Group: read, Others: none",
              "Owner: read only, Group: read+write, Others: none",
              "Owner: read+write+execute, Group: read, Others: none",
              "Owner: read+write, Group: read+execute, Others: none"],
             "Owner: read+write, Group: read, Others: none",
             "6=rw-, 4=r--, 0=---.",
             ["linux", "permissions"]),
        _tf("Linux", "easy",
            "In Linux, PID 1 is typically the init/system manager process.",
            True,
            "PID 1 is commonly systemd or another init process.",
            ["linux", "systemd"]),
        _sa("Linux", "hard",
            "What is the Linux command to follow (tail) a log file continuously?",
            "tail -f",
            "`tail -f /path/to/log` follows new lines as they are appended.",
            ["linux", "logs"]),

        _mcq("Networking", "easy",
             "Which port does HTTPS typically use?",
             ["443", "80", "22", "53"],
             "443",
             "HTTPS is typically TCP port 443.",
             ["networking", "http"]),
        _mcq("Networking", "medium",
             "What is the main purpose of a load balancer?",
             ["Distribute traffic across multiple backends",
              "Encrypt all data at rest",
              "Replace DNS",
              "Compress log files"],
             "Distribute traffic across multiple backends",
             "Load balancers spread traffic to improve availability and performance.",
             ["networking", "lb"]),
        _tf("Networking", "medium",
            "A 502 status code generally indicates the gateway/proxy received an invalid response from the upstream server.",
            True,
            "Often seen when upstream is down or misbehaving behind a proxy.",
            ["networking", "http", "reverse-proxy"]),

        _mcq("CI/CD", "medium",
             "Continuous Integration primarily means:",
             ["Merging code frequently into a shared repository with automated checks",
              "Deploying to production after every commit with no tests",
              "Only writing infrastructure as code",
              "Using containers exclusively"],
             "Merging code frequently into a shared repository with automated checks",
             "CI encourages frequent merges validated by automated builds/tests.",
             ["cicd", "ci"]),
        _mcq("CI/CD", "medium",
             "Which practice best reduces risk in deployments?",
             ["Small, frequent releases",
              "Large quarterly releases",
              "Manual deployments only",
              "Disabling monitoring"],
             "Small, frequent releases",
             "Smaller batches reduce blast radius and speed rollback.",
             ["cicd", "release"]),
        _tf("CI/CD", "easy",
            "A CD pipeline can include automated tests and deployment steps.",
            True,
            "CD often includes build, test, deploy, verify stages.",
            ["cicd", "cd"]),
        _sa("CI/CD", "hard",
            "Name one deployment strategy that reduces downtime by shifting traffic between environments.",
            "blue-green",
            "Blue-green uses two environments; traffic shifts from blue to green.",
            ["cicd", "deployment", "strategy"]),

        _mcq("Containers", "easy",
             "Which Docker command builds an image from a Dockerfile?",
             ["docker build", "docker run", "docker start", "docker pull --build"],
             "docker build",
             "`docker build` builds an image from Dockerfile instructions.",
             ["docker", "containers"]),
        _mcq("Containers", "medium",
             "What is the key difference between a container and a VM?",
             ["Containers share the host OS kernel; VMs include a full guest OS",
              "Containers always run faster than VMs in every case",
              "VMs cannot be automated",
              "Containers do not use namespaces/cgroups"],
             "Containers share the host OS kernel; VMs include a full guest OS",
             "Containers are OS-level virtualization; VMs are hardware virtualization.",
             ["docker", "virtualization"]),
        _tf("Containers", "medium",
            "A Docker image is an immutable template used to create containers.",
            True,
            "Images are built layers; containers are runtime instances.",
            ["docker", "containers"]),
        _sa("Containers", "easy",
            "What file commonly defines multi-container apps for Docker (classic usage)?",
            "docker-compose.yml",
            "Compose files define multi-container services, networks, and volumes.",
            ["docker", "compose"]),

        _mcq("Kubernetes", "medium",
             "Which Kubernetes object maintains a desired number of replica Pods?",
             ["Deployment", "Service", "ConfigMap", "Namespace"],
             "Deployment",
             "Deployments manage ReplicaSets and keep replica count stable.",
             ["kubernetes", "workloads"]),
        _mcq("Kubernetes", "medium",
             "What does a Kubernetes Service primarily provide?",
             ["Stable networking and load-balancing for a set of Pods",
              "A VM to run Pods on",
              "A container image registry",
              "A secret store for cloud credentials"],
             "Stable networking and load-balancing for a set of Pods",
             "Services select Pods via labels and provide a stable endpoint.",
             ["kubernetes", "networking"]),
        _tf("Kubernetes", "medium",
            "A ConfigMap is intended for non-sensitive configuration data.",
            True,
            "Secrets are intended for sensitive values (with proper protection).",
            ["kubernetes", "config"]),
        _sa("Kubernetes", "hard",
            "Name the Kubernetes component that schedules Pods onto Nodes.",
            "kube-scheduler",
            "kube-scheduler chooses Nodes for Pods based on constraints and resources.",
            ["kubernetes", "control-plane"]),

        _mcq("Infrastructure as Code", "medium",
             "In Terraform, what is the purpose of the state file?",
             ["Track real-world resources managed by Terraform",
              "Store container layers",
              "Replace version control",
              "Encrypt all provider APIs"],
             "Track real-world resources managed by Terraform",
             "Terraform state maps resources in code to real infrastructure objects.",
             ["iac", "terraform"]),
        _mcq("Infrastructure as Code", "easy",
             "Which tool is primarily used for configuration management via playbooks?",
             ["Ansible", "Terraform", "Docker", "Prometheus"],
             "Ansible",
             "Ansible uses playbooks (YAML) to configure systems.",
             ["iac", "ansible"]),
        _tf("Infrastructure as Code", "medium",
            "Idempotency means running the same automation repeatedly results in the same final state.",
            True,
            "Idempotent tasks avoid unintended side effects on repeated runs.",
            ["iac", "automation"]),
        _sa("Infrastructure as Code", "hard",
            "In Terraform, what command previews changes without applying them?",
            "terraform plan",
            "`terraform plan` shows the execution plan.",
            ["iac", "terraform"]),

        _mcq("Observability", "easy",
             "Which is a common time-series monitoring system?",
             ["Prometheus", "MySQL", "Nginx", "Make"],
             "Prometheus",
             "Prometheus scrapes metrics and stores them as time-series data.",
             ["observability", "metrics"]),
        _mcq("Observability", "medium",
             "What does MTTR typically stand for in incident response?",
             ["Mean Time To Recovery",
              "Maximum Time To Retry",
              "Mean Time To Release",
              "Minimum Time To Restore"],
             "Mean Time To Recovery",
             "MTTR is commonly used as Mean Time To Recovery/Restore.",
             ["observability", "reliability"]),
        _tf("Observability", "medium",
            "Tracing helps identify latency and call paths across distributed services.",
            True,
            "Distributed tracing follows requests across services.",
            ["observability", "tracing"]),
        _sa("Observability", "medium",
            "Name one common log aggregation/search tool.",
            "splunk",
            "Splunk, Elastic/ELK, Loki, etc. are common solutions.",
            ["observability", "logging"]),

        _mcq("Security", "medium",
             "What is the principle of least privilege?",
             ["Grant only the permissions needed to perform a task",
              "Grant admin permissions to speed up work",
              "Use the same password everywhere",
              "Disable MFA for automation"],
             "Grant only the permissions needed to perform a task",
             "Least privilege limits blast radius and reduces risk.",
             ["security", "iam"]),
        _tf("Security", "easy",
            "Secrets should be stored in plaintext inside Git repositories.",
            False,
            "Use secret managers, vaults, and CI secret stores.",
            ["security", "secrets"]),
        _sa("Security", "hard",
            "Name one common software supply chain security practice for CI pipelines.",
            "dependency scanning",
            "Examples: dependency scanning, SBOM, signing artifacts, SAST/DAST.",
            ["security", "supply-chain", "cicd"]),
    ]
    return T


def build_extra_blocks() -> List[List[Dict[str, Any]]]:
    blocks: List[List[Dict[str, Any]]] = []

    blocks.append([
        _mcq("Version Control", "medium",
             "Which command shows a commit history graph with branches in a compact form?",
             ["git log --oneline --graph --decorate", "git graph", "git history --tree", "git show --graph-only"],
             "git log --oneline --graph --decorate",
             "A common way to visualize commit history in the terminal.",
             ["git", "history"]),
        _mcq("Version Control", "hard",
             "What is a common risk of rebasing a branch that others are already using?",
             ["It rewrites history and can cause conflicts for collaborators",
              "It automatically deletes untracked files",
              "It disables hooks permanently",
              "It forces Git LFS for all files"],
             "It rewrites history and can cause conflicts for collaborators",
             "Rebasing shared branches can break others' history and require recovery steps.",
             ["git", "collaboration"]),
        _sa("Version Control", "easy",
            "What Git command downloads remote commits and updates remote-tracking branches without merging?",
            "git fetch",
            "`git fetch` updates remote-tracking branches without modifying your current branch.",
            ["git"]),
    ])

    blocks.append([
        _mcq("Linux", "medium",
             "Which command shows disk usage for a directory in a human-readable summary?",
             ["du -sh /path", "df -h /path", "ls -lh /path", "stat -h /path"],
             "du -sh /path",
             "`du -sh` summarizes directory size.",
             ["linux", "storage"]),
        _mcq("Linux", "hard",
             "Which systemd command shows logs for a service unit?",
             ["journalctl -u <unit>", "systemctl logs <unit>", "dmesg -u <unit>", "logctl -u <unit>"],
             "journalctl -u <unit>",
             "journalctl queries systemd-journald logs; -u filters by unit.",
             ["linux", "systemd", "logs"]),
        _tf("Linux", "medium",
            "In Linux, `kill -9` sends SIGKILL which cannot be caught or ignored by the process.",
            True,
            "SIGKILL is immediate and uncatchable; use with caution.",
            ["linux", "signals"]),
    ])

    blocks.append([
        _mcq("Containers", "medium",
             "Which Dockerfile instruction is typically used to specify the base image?",
             ["FROM", "BASE", "IMAGE", "START"],
             "FROM",
             "FROM sets the base image layer.",
             ["docker", "dockerfile"]),
        _mcq("Containers", "hard",
             "What is a primary reason to use multi-stage Docker builds?",
             ["Reduce final image size by copying only required artifacts",
              "Run multiple containers on one host",
              "Avoid using any package managers",
              "Force containers to run as root"],
             "Reduce final image size by copying only required artifacts",
             "Multi-stage builds separate build and runtime environments.",
             ["docker", "optimization"]),
        _sa("Containers", "easy",
            "What Docker command lists running containers?",
            "docker ps",
            "`docker ps` shows running containers; add -a for all.",
            ["docker"]),
    ])

    blocks.append([
        _mcq("Kubernetes", "medium",
             "Which Kubernetes object stores sensitive data such as passwords and tokens?",
             ["Secret", "ConfigMap", "Deployment", "Ingress"],
             "Secret",
             "Secrets are intended for sensitive configuration values.",
             ["kubernetes", "security"]),
        _mcq("Kubernetes", "hard",
             "What is the primary role of an Ingress controller?",
             ["Implement HTTP(S) routing rules defined by Ingress resources",
              "Schedule Pods on Nodes",
              "Store cluster secrets",
              "Manage container images"],
             "Implement HTTP(S) routing rules defined by Ingress resources",
             "Ingress resources require a controller to realize routing.",
             ["kubernetes", "networking", "ingress"]),
        _sa("Kubernetes", "medium",
            "What kubectl command shows detailed information about a Pod including events?",
            "kubectl describe pod",
            "`kubectl describe pod <name>` shows details and recent events.",
            ["kubernetes", "kubectl"]),
    ])

    blocks.append([
        _mcq("Infrastructure as Code", "medium",
             "Which Terraform command downloads provider plugins and modules?",
             ["terraform init", "terraform get-only", "terraform download", "terraform module install"],
             "terraform init",
             "`terraform init` initializes the working directory and downloads providers/modules.",
             ["terraform", "iac"]),
        _tf("Infrastructure as Code", "hard",
            "Terraform modules are a way to package and reuse Terraform configuration.",
            True,
            "Modules improve reuse and maintainability.",
            ["terraform", "modules"]),
        _sa("Infrastructure as Code", "medium",
            "Name one benefit of storing Terraform state remotely (e.g., S3, Terraform Cloud).",
            "locking",
            "Remote state enables collaboration features like locking and shared access.",
            ["terraform", "state"]),
    ])

    blocks.append([
        _mcq("Observability", "medium",
             "Which term describes the number of requests served per unit time?",
             ["Throughput", "Latency", "Saturation", "Availability"],
             "Throughput",
             "Throughput measures rate; latency measures time per request.",
             ["observability", "performance"]),
        _mcq("Observability", "hard",
             "What is a common Prometheus metric type that only increases (except reset)?",
             ["Counter", "Gauge", "Histogram", "Summary"],
             "Counter",
             "Counters are monotonically increasing values.",
             ["prometheus", "metrics"]),
        _tf("Observability", "easy",
            "A dashboard is a substitute for alerting.",
            False,
            "Dashboards help visualize; alerting notifies on issues.",
            ["observability", "alerting"]),
    ])

    blocks.append([
        _mcq("Security", "medium",
             "What does MFA stand for?",
             ["Multi-Factor Authentication", "Managed Firewall Access", "Mainframe File Audit", "Multi-Failover Authorization"],
             "Multi-Factor Authentication",
             "MFA uses two or more factors to authenticate users.",
             ["security", "iam"]),
        _mcq("Security", "hard",
             "Which practice helps ensure only trusted code is deployed by verifying artifact integrity?",
             ["Signing artifacts", "Disabling logs", "Using larger instances", "Turning off TLS"],
             "Signing artifacts",
             "Artifact signing helps verify provenance and integrity in the supply chain.",
             ["security", "supply-chain"]),
        _tf("Security", "medium",
            "Least privilege can reduce the blast radius of a compromised credential.",
            True,
            "Fewer permissions limit what an attacker can do.",
            ["security", "iam"]),
    ])

    blocks.append([
        _mcq("Cloud", "easy",
             "What is elasticity in cloud computing?",
             ["Ability to scale resources up/down based on demand",
              "Using only reserved instances",
              "Storing data only on-prem",
              "Encrypting all traffic by default"],
             "Ability to scale resources up/down based on demand",
             "Elasticity is scaling with demand.",
             ["cloud", "scaling"]),
        _mcq("Cloud", "medium",
             "What is the shared responsibility model?",
             ["Cloud provider and customer share security responsibilities",
              "Customer is responsible for everything",
              "Provider is responsible for everything including app code",
              "Only applies to private clouds"],
             "Cloud provider and customer share security responsibilities",
             "Responsibilities vary by service type (IaaS/PaaS/SaaS).",
             ["cloud", "security"]),
        _tf("Cloud", "medium",
            "In IaaS, customers are typically responsible for patching the guest OS.",
            True,
            "In many IaaS models, OS patching is the customer's responsibility.",
            ["cloud", "iaas"]),
    ])

    # Breadth categories (smaller)
    blocks.append([
        _mcq("Testing", "medium",
             "Which test type validates how components work together end-to-end?",
             ["Integration testing", "Unit testing", "Linting", "Static analysis only"],
             "Integration testing",
             "Integration tests verify interactions between components.",
             ["testing", "quality"]),
        _mcq("HTTP", "easy",
             "Which HTTP method is generally used to retrieve a resource?",
             ["GET", "POST", "PUT", "PATCH"],
             "GET",
             "GET is used for retrieval and should be idempotent.",
             ["http", "api"]),
        _tf("Reliability", "hard",
            "An SLO is the same thing as an SLA.",
            False,
            "SLO is an internal target; SLA is an external contract/commitment.",
            ["sre", "reliability"]),
        _sa("Automation", "easy",
            "Name one reason to automate repetitive operational tasks.",
            "reduce errors",
            "Automation reduces human error and improves repeatability.",
            ["automation"]),
        _mcq("Release", "hard",
             "Which practice releases features to users gradually to reduce risk?",
             ["Canary release", "Big bang deployment", "Manual copy to prod", "Disable rollbacks"],
             "Canary release",
             "Canary deploys to a small subset first, then expands.",
             ["cicd", "deployment", "strategy"]),
    ])

    return blocks


def slugify_category(name: str) -> str:
    # Title-case words separated by underscores, safe for filenames
    s = re.sub(r"[^\w\s-]", "", name).strip()
    s = re.sub(r"[\s-]+", "_", s)
    return s


def vary_text(s: str, variant_i: int) -> str:
    swaps = [
        ("primarily", "mainly"),
        ("typically", "commonly"),
        ("purpose", "role"),
        ("command", "CLI command"),
        ("primary", "main"),
    ]
    out = s
    if variant_i % 2 == 1:
        for a, b in swaps[:2]:
            out = out.replace(a, b)
    if variant_i % 3 == 0:
        for a, b in swaps[2:4]:
            out = out.replace(a, b)
    return out


def clone_with_variation(q: Dict[str, Any], variant_i: int, *, rng: random.Random) -> Dict[str, Any]:
    qq = dict(q)
    qq["question"] = vary_text(qq["question"], variant_i)
    qq["explanation"] = vary_text(qq["explanation"], variant_i)
    if qq["type"] == "mcq" and qq.get("options"):
        opts = list(qq["options"])
        rng.shuffle(opts)
        qq["options"] = opts
    return qq


def expand_to_200(*, seed: List[Dict[str, Any]], rng: random.Random) -> List[Question]:
    # Targets
    targets = {"easy": 80, "medium": 80, "hard": 40}

    def count_by_difficulty(items: List[Dict[str, Any]]) -> Dict[str, int]:
        c = {"easy": 0, "medium": 0, "hard": 0}
        for it in items:
            c[it["difficulty"]] += 1
        return c

    def is_advanced(q: Dict[str, Any]) -> bool:
        advanced_tags = {"supply-chain", "ingress", "modules", "state", "sre", "tracing", "optimization"}
        return any(t in advanced_tags for t in q.get("tags", []))

    def is_basic(q: Dict[str, Any]) -> bool:
        basic_tags = {"devops", "culture", "http", "api", "docker", "git", "linux"}
        return any(t in basic_tags for t in q.get("tags", []))

    pool: List[Dict[str, Any]] = list(seed)
    blocks = build_extra_blocks()

    variant_counter = 1
    while len(pool) < 200:
        current = count_by_difficulty(pool)
        desired = sorted(targets.keys(), key=lambda d: (targets[d] - current[d]), reverse=True)[0]

        rng.shuffle(blocks)
        added = False
        for block in blocks:
            candidates = [q for q in block if q["difficulty"] == desired]
            if not candidates:
                continue
            base = rng.choice(candidates)
            pool.append(clone_with_variation(base, variant_counter, rng=rng))
            variant_counter += 1
            added = True
            break

        if not added:
            base = rng.choice(rng.choice(blocks))
            pool.append(clone_with_variation(base, variant_counter, rng=rng))
            variant_counter += 1

        if len(pool) > 200:
            pool = pool[:200]

    # Rebalance labels to match targets (light-touch)
    def counts() -> Dict[str, int]:
        c = {"easy": 0, "medium": 0, "hard": 0}
        for q in pool:
            c[q["difficulty"]] += 1
        return c

    for _ in range(500):
        c = counts()
        if c == targets:
            break

        if c["hard"] < targets["hard"]:
            mids = [q for q in pool if q["difficulty"] == "medium" and is_advanced(q)] or \
                   [q for q in pool if q["difficulty"] == "medium"]
            rng.choice(mids)["difficulty"] = "hard"
            continue

        if c["hard"] > targets["hard"]:
            hards = [q for q in pool if q["difficulty"] == "hard" and is_basic(q)] or \
                    [q for q in pool if q["difficulty"] == "hard"]
            rng.choice(hards)["difficulty"] = "medium"
            continue

        if c["easy"] < targets["easy"]:
            meds = [q for q in pool if q["difficulty"] == "medium" and is_basic(q)] or \
                   [q for q in pool if q["difficulty"] == "medium"]
            rng.choice(meds)["difficulty"] = "easy"
            continue

        if c["easy"] > targets["easy"]:
            easies = [q for q in pool if q["difficulty"] == "easy" and not is_basic(q)] or \
                     [q for q in pool if q["difficulty"] == "easy"]
            rng.choice(easies)["difficulty"] = "medium"
            continue

        # Adjust medium as needed if still off
        if c["medium"] < targets["medium"]:
            rng.choice([q for q in pool if q["difficulty"] == "easy"])["difficulty"] = "medium"
        elif c["medium"] > targets["medium"]:
            rng.choice([q for q in pool if q["difficulty"] == "medium"])["difficulty"] = "easy"

    # Assign global IDs
    questions: List[Question] = []
    for i, q in enumerate(pool, start=1):
        questions.append(
            Question(
                id=i,
                category=q["category"],
                difficulty=q["difficulty"],
                type=q["type"],
                question=q["question"],
                options=q.get("options"),
                answer=q["answer"],
                explanation=q.get("explanation", ""),
                tags=q.get("tags", []),
            )
        )
    return questions


def write_split_files(questions: List[Question], out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)

    by_cat: Dict[str, List[Question]] = {}
    for q in questions:
        by_cat.setdefault(q.category, []).append(q)

    # Write each category file
    category_files: Dict[str, str] = {}
    for cat, items in sorted(by_cat.items(), key=lambda kv: kv[0].lower()):
        fname = f"{slugify_category(cat)}.json"
        path = os.path.join(out_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump([asdict(x) for x in items], f, indent=2, ensure_ascii=False)
        category_files[cat] = fname

    # Write index.json with summary
    by_diff = {"easy": 0, "medium": 0, "hard": 0}
    by_type = {"mcq": 0, "true_false": 0, "short_answer": 0}
    for q in questions:
        by_diff[q.difficulty] += 1
        by_type[q.type] += 1

    index = {
        "total_questions": len(questions),
        "difficulty_distribution": by_diff,
        "type_distribution": by_type,
        "categories": [
            {
                "category": cat,
                "file": category_files[cat],
                "count": len(by_cat[cat]),
            }
            for cat in sorted(category_files.keys(), key=lambda s: s.lower())
        ],
    }

    with open(os.path.join(out_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a 200-question DevOps quiz bank split into category JSON files.")
    ap.add_argument("-d", "--out-dir", default="devops_bank", help="Output directory")
    ap.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    seed = build_seed_templates()
    questions = expand_to_200(seed=seed, rng=rng)
    write_split_files(questions, args.out_dir)

    print(f"Wrote {len(questions)} questions into folder: {args.out_dir}")
    print(f"Index file: {os.path.join(args.out_dir, 'index.json')}")


if __name__ == "__main__":
    main()
