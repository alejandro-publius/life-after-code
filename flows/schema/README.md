# GitLab flow schema (vendored copies)

Read on 2026-10-06 so CI can validate our flows offline.

- `flow_v2.json`: GitLab's JSON schema for custom flows, from
  https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/validators/json_schemas/ai_catalog/flow_v2.json
- `tools.json`: the tool names a flow component may use, from
  https://gitlab.com/components/ai-catalog/-/blob/main/schemas/component/tools.json

Both belong to GitLab and keep their upstream licences. Refresh them with `python flows/validate.py --refresh`.
