# Agent commands for repeated runs (sourced by run scripts). Each runs with cwd = packet sandbox.
export PSAB_AGENTS=<agents>
export TAGME_PROXY_KEY=local-proxy
PROMPT_OC="Read instructions.md and task.json. Solve the executable benchmark task. Write only submission.json as valid JSON. Do not modify other files."
PROMPT_CODEX="Read instructions.md and task.json. Solve the executable benchmark task. Write valid JSON exactly to submission.json in the current directory. Do not modify other files. Do not output Markdown."
PROMPT_CURSOR="Read instructions.md and task.json in the current directory. Solve the executable benchmark task. Write valid JSON exactly to submission.json in the current directory. Do not modify other files."

cmd_codex() {
  # Fresh CODEX_HOME per case: no memories or session state carried between runs.
  echo "H=$PSAB_AGENTS/homes/codex/\$(basename \"\$BENCH_PACKET_DIR\") && mkdir -p \"\$H\" && cp $PSAB_AGENTS/codex-home/config.toml \"\$H/\" && CODEX_HOME=\"\$H\" TAGME_PROXY_KEY=local-proxy $PSAB_AGENTS/npm/node_modules/.bin/codex exec --skip-git-repo-check --sandbox workspace-write --cd \"\$BENCH_PACKET_DIR\" \"$PROMPT_CODEX\""
}
cmd_cursor() {
  # Cursor's API is region-blocked on the host route; run it in the VM's VPN namespace.
  echo "cd \"\$BENCH_PACKET_DIR\" && ip netns exec hermes-vpn $PSAB_AGENTS/cursor/dist-package/cursor-agent -p --force --model composer-2.5 \"$PROMPT_CURSOR\""
}
cmd_opencode() {  # $1 = TagMe model id, e.g. deepseek/deepseek-v4-flash
  # Fresh data/state dirs per case: no session database shared between runs.
  echo "D=$PSAB_AGENTS/homes/oc/\$(basename \"\$BENCH_PACKET_DIR\") && XDG_CONFIG_HOME=$PSAB_AGENTS/oc/config XDG_DATA_HOME=\"\$D/data\" XDG_STATE_HOME=\"\$D/state\" XDG_CACHE_HOME=$PSAB_AGENTS/oc/cache $PSAB_AGENTS/npm/node_modules/.bin/opencode run --model tagme/$1 --dir \"\$BENCH_PACKET_DIR\" \"$PROMPT_OC\""
}
cmd_aider() {  # $1 = TagMe model id
  echo "A=$PSAB_AGENTS/homes/aider/\$(basename \"\$BENCH_PACKET_DIR\") && mkdir -p \"\$A\" && cd \"\$BENCH_PACKET_DIR\" && OPENAI_API_BASE=http://127.0.0.1:30210/v1 OPENAI_API_KEY=local-proxy HOME=\"\$A\" $PSAB_AGENTS/bin/aider --model openai/$1 --yes-always --no-git --no-auto-commits --no-show-model-warnings --no-check-update --no-analytics --no-pretty --no-stream --message \"$PROMPT_OC\" instructions.md task.json submission.json"
}

# OpenRouter route (personal key) for models that TagMe cannot serve. OpenRouter rejects the
# host IP, so these agents run in the VM's VPN namespace and call OpenRouter directly.
# The key is read from a 0600 file at run time and never appears in the command or logs.
OR_ENV='set -a; . <home>/secrets/openrouter.env; set +a'
cmd_opencode_or() {  # $1 = OpenRouter model id
  echo "$OR_ENV; D=$PSAB_AGENTS/homes/oc/\$(basename \"\$BENCH_PACKET_DIR\") && XDG_CONFIG_HOME=$PSAB_AGENTS/oc/config XDG_DATA_HOME=\"\$D/data\" XDG_STATE_HOME=\"\$D/state\" XDG_CACHE_HOME=$PSAB_AGENTS/oc/cache ip netns exec hermes-vpn $PSAB_AGENTS/npm/node_modules/.bin/opencode run --model openrouter-direct/$1 --dir \"\$BENCH_PACKET_DIR\" \"$PROMPT_OC\""
}
cmd_aider_or() {  # $1 = OpenRouter model id
  echo "$OR_ENV; A=$PSAB_AGENTS/homes/aider/\$(basename \"\$BENCH_PACKET_DIR\") && mkdir -p \"\$A\" && cd \"\$BENCH_PACKET_DIR\" && OPENAI_API_BASE=https://openrouter.ai/api/v1 OPENAI_API_KEY=\"\$OPENROUTER_API_KEY\" HOME=\"\$A\" ip netns exec hermes-vpn $PSAB_AGENTS/bin/aider --model openai/$1 --yes-always --no-git --no-auto-commits --no-show-model-warnings --no-check-update --no-analytics --no-pretty --no-stream --message \"$PROMPT_OC\" instructions.md task.json submission.json"
}
