<div align="center">
  <img src="assets/header.svg" width="100%" alt="michal@devops:~$ whoami — Michał Jakubowski, Linux Systems Administrator moving into Cloud / DevOps">

  <a href="https://www.linkedin.com/in/micha%C5%82-jakubowski-46908b43b/">LinkedIn</a> · <a href="#projects">Projects</a> · <a href="#tech-stack">Tech stack</a>
</div>

### `$ whoami`

<img src="assets/neofetch.svg" width="100%" alt="neofetch-style card: Linux Systems Administrator, focus on Cloud, DevOps and GitOps, live GitHub statistics">

At work I run Linux infrastructure on KVM and VMware vCenter and take part in an AWS Landing Zone rollout with Terraform and Entra ID SSO. Outside work I build the same small platform three times, on a VPS, on AWS and on Kubernetes, and make CI prove each one works before I call it done.

### `$ cat focus.md`

<img src="assets/path.svg" width="100%" alt="Project path: VPS with Ansible and Docker, then AWS with Terraform and SSM, then Kubernetes with Argo CD">

- **Everything as code:** Terraform, Ansible, Helm and Kustomize. Nothing on a server is configured by hand.
- **CI that proves it:** the second Ansible run must report `changed=0`, IAM permissions are checked in the policy simulator, and every Kubernetes commit runs end-to-end on a fresh kind cluster.
- **Secure defaults:** OIDC instead of stored cloud keys, SSM instead of SSH, Sealed Secrets, least-privilege roles.
- **Observability built in:** Prometheus, Grafana and Uptime Kuma are provisioned together with the services.
- **Next:** AWS Certified Cloud Practitioner (planned 11.2026), then RHCSA (planned 01.2027).

<a id="projects"></a>

### `$ ls ~/projects`

<a href="https://github.com/michaljakubowski2001/mikrus-devops-portfolio"><img src="assets/project-mikrus-devops-portfolio.svg" width="100%" alt="01 VPS — DevOps Platform on a 2 GB VPS"></a>

Six self-hosted services managed by Ansible and Docker. Every push deploys and fails unless the second Ansible run reports `changed=0`.<br>
[![Validate and deploy](https://github.com/michaljakubowski2001/mikrus-devops-portfolio/actions/workflows/deploy.yml/badge.svg)](https://github.com/michaljakubowski2001/mikrus-devops-portfolio/actions/workflows/deploy.yml)

<a href="https://github.com/michaljakubowski2001/aws-devops-portfolio"><img src="assets/project-aws-devops-portfolio.svg" width="100%" alt="02 AWS — AWS Infrastructure Automation"></a>

The same Ansible roles on AWS. Terraform, OIDC instead of keys, SSM instead of SSH, a least-privilege role tested in the IAM policy simulator.<br>
[![Production apply](https://github.com/michaljakubowski2001/aws-devops-portfolio/actions/workflows/apply.yml/badge.svg)](https://github.com/michaljakubowski2001/aws-devops-portfolio/actions/workflows/apply.yml)

<a href="https://github.com/michaljakubowski2001/k8s-gitops-portfolio"><img src="assets/project-k8s-gitops-portfolio.svg" width="100%" alt="03 Kubernetes — Kubernetes GitOps Platform"></a>

The same services on Kubernetes, deployed only by Argo CD. Every commit builds a kind cluster in CI and runs 13 end-to-end checks.<br>
[![GitOps end-to-end](https://github.com/michaljakubowski2001/k8s-gitops-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/michaljakubowski2001/k8s-gitops-portfolio/actions/workflows/ci.yml)

<a id="tech-stack"></a>

### `$ tech-stack --list`

<img src="assets/stack.svg" width="100%" alt="Tech stack: Linux, KVM, VMware vCenter, FreeIPA, Terraform, Ansible, Packer, AWS, Docker, Kubernetes, Helm, Kustomize, GitHub Actions, Argo CD, Prometheus, Grafana, Uptime Kuma, Zabbix, Fortinet, DNS, VLAN">

### `$ git log --graph`

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/michaljakubowski2001/michaljakubowski2001/output/github-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/michaljakubowski2001/michaljakubowski2001/output/github-snake.svg">
  <img src="https://raw.githubusercontent.com/michaljakubowski2001/michaljakubowski2001/output/github-snake-dark.svg" width="100%" alt="Contribution graph eaten by a snake">
</picture>

<sub>Every image above is an SVG rendered from <a href="profile.json"><code>profile.json</code></a> and the GitHub API by <a href="scripts/render.py"><code>scripts/render.py</code></a>, refreshed daily by <a href=".github/workflows/profile.yml">GitHub Actions</a>.</sub>
