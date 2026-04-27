#!/usr/bin/env bash
# ============================================================
#  OpenKimo 一键部署脚本
#  - 检查 Docker / Docker Compose 环境
#  - 终端交互式向导生成 .env
#  - 构建镜像并启动容器
# ============================================================
set -euo pipefail

# ---------------- ANSI Colors ----------------
if [ -t 1 ]; then
  C_RESET='\033[0m'
  C_BOLD='\033[1m'
  C_DIM='\033[2m'
  C_RED='\033[31m'
  C_GREEN='\033[32m'
  C_YELLOW='\033[33m'
  C_BLUE='\033[34m'
  C_MAGENTA='\033[35m'
  C_CYAN='\033[36m'
else
  C_RESET=''; C_BOLD=''; C_DIM=''
  C_RED=''; C_GREEN=''; C_YELLOW=''
  C_BLUE=''; C_MAGENTA=''; C_CYAN=''
fi

# ---------------- Paths ----------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
ENV_EXAMPLE="$PROJECT_ROOT/.env.example"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

cd "$PROJECT_ROOT"

# ---------------- UI Helpers ----------------
hr() { printf "${C_DIM}%s${C_RESET}\n" "------------------------------------------------------------"; }

banner() {
  printf "${C_CYAN}${C_BOLD}"
  cat <<'EOF'
   ___                  _  ___
  / _ \ _ __   ___ _ __| |/ (_)_ __ ___   ___
 | | | | '_ \ / _ \ '_ \ ' /| | '_ ` _ \ / _ \
 | |_| | |_) |  __/ | | . \ | | | | | | | (_) |
  \___/| .__/ \___|_| |_|_|\_\_|_| |_| |_|\___/
       |_|        One Docker. Zero Worries.
EOF
  printf "${C_RESET}\n"
}

section() {
  echo
  printf "${C_MAGENTA}${C_BOLD}▸ %s${C_RESET}\n" "$1"
  hr
}

info()    { printf "${C_BLUE}ℹ${C_RESET}  %s\n" "$*"; }
ok()      { printf "${C_GREEN}✔${C_RESET}  %s\n" "$*"; }
warn()    { printf "${C_YELLOW}⚠${C_RESET}  %s\n" "$*"; }
err()     { printf "${C_RED}✖${C_RESET}  %s\n" "$*" >&2; }

# Read with default value. Usage: ask VAR "Prompt" "default"
ask() {
  local __var="$1"; local __prompt="$2"; local __default="${3:-}"
  local __input
  if [ -n "$__default" ]; then
    printf "${C_BOLD}?${C_RESET} %s ${C_DIM}[%s]${C_RESET}: " "$__prompt" "$__default"
  else
    printf "${C_BOLD}?${C_RESET} %s: " "$__prompt"
  fi
  IFS= read -r __input || true
  printf -v "$__var" "%s" "${__input:-$__default}"
}

# Read secret (no echo). Usage: ask_secret VAR "Prompt"
ask_secret() {
  local __var="$1"; local __prompt="$2"
  local __input
  printf "${C_BOLD}?${C_RESET} %s ${C_DIM}(隐藏输入, 回车跳过)${C_RESET}: " "$__prompt"
  IFS= read -rs __input || true
  echo
  printf -v "$__var" "%s" "$__input"
}

# Yes/No prompt. Usage: ask_yn VAR "Prompt" "y|n"
ask_yn() {
  local __var="$1"; local __prompt="$2"; local __default="${3:-n}"
  local __hint __input
  case "$__default" in
    y|Y) __hint="Y/n" ;;
    *)   __hint="y/N" ;;
  esac
  while true; do
    printf "${C_BOLD}?${C_RESET} %s ${C_DIM}[%s]${C_RESET}: " "$__prompt" "$__hint"
    IFS= read -r __input || true
    __input="${__input:-$__default}"
    case "$__input" in
      y|Y|yes|YES) printf -v "$__var" "true";  return 0 ;;
      n|N|no|NO)   printf -v "$__var" "false"; return 0 ;;
      *) warn "请输入 y 或 n" ;;
    esac
  done
}

# Single-choice menu. Usage: ask_choice VAR "Prompt" "opt1" "opt2" ...
ask_choice() {
  local __var="$1"; local __prompt="$2"; shift 2
  local __opts=("$@")
  local i __input
  echo
  printf "${C_BOLD}?${C_RESET} %s\n" "$__prompt"
  for i in "${!__opts[@]}"; do
    printf "    ${C_CYAN}%d)${C_RESET} %s\n" "$((i+1))" "${__opts[$i]}"
  done
  while true; do
    printf "  选择 ${C_DIM}[1-%d, 默认 1]${C_RESET}: " "${#__opts[@]}"
    IFS= read -r __input || true
    __input="${__input:-1}"
    if [[ "$__input" =~ ^[0-9]+$ ]] && [ "$__input" -ge 1 ] && [ "$__input" -le "${#__opts[@]}" ]; then
      printf -v "$__var" "%s" "${__opts[$((__input-1))]}"
      return 0
    fi
    warn "无效选项"
  done
}

random_token() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 32
  else
    head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n'
  fi
}

# ---------------- Prerequisite Check ----------------
check_prereqs() {
  section "环境检测"
  local missing=0

  if command -v docker >/dev/null 2>&1; then
    ok "docker: $(docker --version)"
  else
    err "未找到 docker，请先安装 Docker Engine: https://docs.docker.com/get-docker/"
    missing=1
  fi

  if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
    ok "compose: $(docker compose version --short 2>/dev/null || echo plugin)"
  elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
    ok "compose: $(docker-compose version --short)"
  else
    err "未找到 docker compose，请安装: https://docs.docker.com/compose/install/"
    missing=1
  fi

  if ! docker info >/dev/null 2>&1; then
    err "Docker daemon 未运行，请启动 Docker Desktop / dockerd 后重试"
    missing=1
  fi

  [ "$missing" -eq 0 ] || exit 1
}

# ---------------- .env Onboarding ----------------
onboard_env() {
  section ".env 配置向导"

  if [ -f "$ENV_FILE" ]; then
    warn "已存在 .env 文件: $ENV_FILE"
    local _overwrite
    ask_yn _overwrite "是否覆盖现有配置？(选择 n 将保留现有 .env)" "n"
    if [ "$_overwrite" != "true" ]; then
      info "保留现有 .env，跳过向导"
      return 0
    fi
    cp "$ENV_FILE" "$ENV_FILE.bak.$(date +%Y%m%d%H%M%S)"
    ok "已备份原配置到 .env.bak.*"
  fi

  # ---- LLM Provider ----
  echo
  info "至少需要配置一个 LLM Provider 的 API Key"
  ask_choice LLM_PROVIDER "请选择默认 LLM Provider" \
    "kimi" "openai" "anthropic"

  KIMI_API_KEY=""; OPENAI_API_KEY=""; ANTHROPIC_API_KEY=""
  KIMI_BASE_URL="https://api.moonshot.cn/v1"
  KIMI_MODEL_NAME="kimi-k2"
  KIMI_MODEL_MAX_CONTEXT_SIZE="262144"
  OPENAI_BASE_URL="https://api.openai.com/v1"
  ANTHROPIC_BASE_URL="https://api.anthropic.com"

  echo
  info "现在录入 API Key（隐藏输入；非默认 provider 也可填，留空跳过）"
  case "$LLM_PROVIDER" in
    kimi)
      ask_secret KIMI_API_KEY      "Kimi / Moonshot API Key (必填)"
      ask_secret OPENAI_API_KEY    "OpenAI API Key (可选)"
      ask_secret ANTHROPIC_API_KEY "Anthropic API Key (可选)"
      ask KIMI_BASE_URL  "Kimi Base URL"  "$KIMI_BASE_URL"
      ask KIMI_MODEL_NAME "Kimi 模型名称" "$KIMI_MODEL_NAME"
      ;;
    openai)
      ask_secret OPENAI_API_KEY    "OpenAI API Key (必填)"
      ask_secret KIMI_API_KEY      "Kimi API Key (可选)"
      ask_secret ANTHROPIC_API_KEY "Anthropic API Key (可选)"
      ask OPENAI_BASE_URL "OpenAI Base URL" "$OPENAI_BASE_URL"
      ;;
    anthropic)
      ask_secret ANTHROPIC_API_KEY "Anthropic API Key (必填)"
      ask_secret KIMI_API_KEY      "Kimi API Key (可选)"
      ask_secret OPENAI_API_KEY    "OpenAI API Key (可选)"
      ask ANTHROPIC_BASE_URL "Anthropic Base URL" "$ANTHROPIC_BASE_URL"
      ;;
  esac

  # Validate at least one key
  if [ -z "$KIMI_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    err "至少需要配置一个 API Key"
    exit 1
  fi

  ask LLM_TEMPERATURE "采样温度 (0.0 - 2.0)" "0.7"
  local _thinking
  ask_yn _thinking "启用 thinking 模式？" "n"
  LLM_THINKING="$_thinking"

  # ---- Web Server ----
  section "Web 服务配置"
  ask KIMI_WEB_PORT "Web UI 监听端口" "5494"

  local _gen_token
  ask_yn _gen_token "自动生成强随机 Session Token？(推荐)" "y"
  if [ "$_gen_token" = "true" ]; then
    KIMI_WEB_SESSION_TOKEN="$(random_token)"
    ok "已生成 Token: ${KIMI_WEB_SESSION_TOKEN:0:12}…"
  else
    ask KIMI_WEB_SESSION_TOKEN "自定义 Session Token" "change-me"
  fi

  local _lan_only
  ask_yn _lan_only "仅允许局域网访问？(对外暴露选 n)" "n"
  KIMI_WEB_LAN_ONLY="$_lan_only"

  local _restrict
  ask_yn _restrict "启用敏感 API 限制？(生产环境推荐)" "n"
  KIMI_WEB_RESTRICT_SENSITIVE_APIS="$_restrict"

  # ---- Sandbox Resources ----
  section "Sandbox 资源限制 (回车使用默认)"
  ask SANDBOX_CPU_LIMIT       "每个 session 容器的 CPU 核数" "2"
  ask SANDBOX_MEMORY_LIMIT    "每个 session 容器的内存限制" "4g"
  ask SANDBOX_DISK_LIMIT      "每个 session 容器的磁盘限制" "10g"
  ask MAX_SESSION_CONTAINERS  "最大同时运行的 session 容器数" "50"
  ask SANDBOX_TIMEOUT_SECONDS "容器自动销毁超时 (秒)"        "86400"

  # ---- Optional Mounts ----
  section "可选挂载 (留空跳过)"
  ask CUSTOM_SKILLS_HOST_PATH "自定义 Skill 目录绝对路径" ""
  ask HF_CACHE_HOST_PATH      "HuggingFace 缓存目录绝对路径" ""
  ask KIMI_SESSION_DATA_DIR   "Session 数据持久化目录" "$PROJECT_ROOT/data/sessions"

  # ---- Write .env ----
  section "写入 .env"
  cat > "$ENV_FILE" <<EOF
# Generated by scripts/deploy.sh on $(date '+%Y-%m-%d %H:%M:%S')
# 重新运行 ./scripts/deploy.sh 可重新生成

# ---------------- LLM Providers ----------------
LLM_PROVIDER=$LLM_PROVIDER
LLM_THINKING=$LLM_THINKING
LLM_TEMPERATURE=$LLM_TEMPERATURE

KIMI_API_KEY=$KIMI_API_KEY
KIMI_BASE_URL=$KIMI_BASE_URL
KIMI_MODEL_NAME=$KIMI_MODEL_NAME
KIMI_MODEL_MAX_CONTEXT_SIZE=$KIMI_MODEL_MAX_CONTEXT_SIZE

OPENAI_API_KEY=$OPENAI_API_KEY
OPENAI_BASE_URL=$OPENAI_BASE_URL

ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
ANTHROPIC_BASE_URL=$ANTHROPIC_BASE_URL

# ---------------- Web Server ----------------
KIMI_WEB_PORT=$KIMI_WEB_PORT
KIMI_WEB_SESSION_TOKEN=$KIMI_WEB_SESSION_TOKEN
KIMI_WEB_ALLOWED_ORIGINS=*
KIMI_WEB_ENFORCE_ORIGIN=false
KIMI_WEB_RESTRICT_SENSITIVE_APIS=$KIMI_WEB_RESTRICT_SENSITIVE_APIS
KIMI_WEB_MAX_PUBLIC_PATH_DEPTH=6
KIMI_WEB_LAN_ONLY=$KIMI_WEB_LAN_ONLY

# ---------------- Sandbox ----------------
SANDBOX_IMAGE=kimi-agent-sandbox:latest
SANDBOX_WORK_DIR=/app
MAX_SESSION_CONTAINERS=$MAX_SESSION_CONTAINERS
SANDBOX_CPU_LIMIT=$SANDBOX_CPU_LIMIT
SANDBOX_MEMORY_LIMIT=$SANDBOX_MEMORY_LIMIT
SANDBOX_DISK_LIMIT=$SANDBOX_DISK_LIMIT
SANDBOX_PID_LIMIT=1000
SANDBOX_TIMEOUT_SECONDS=$SANDBOX_TIMEOUT_SECONDS

# ---------------- Feature Flags ----------------
ENABLE_BROWSER=true
ENABLE_JUPYTER=true
ENABLE_SHELL_SANDBOX=true
BLOCK_DANGEROUS_COMMANDS=true

# ---------------- Optional Mounts ----------------
CUSTOM_SKILLS_HOST_PATH=$CUSTOM_SKILLS_HOST_PATH
HF_CACHE_HOST_PATH=$HF_CACHE_HOST_PATH
KIMI_SESSION_DATA_DIR=$KIMI_SESSION_DATA_DIR
EOF
  chmod 600 "$ENV_FILE"
  ok "已写入 $ENV_FILE (权限 600)"

  # Ensure session data dir exists
  if [ -n "${KIMI_SESSION_DATA_DIR:-}" ]; then
    mkdir -p "$KIMI_SESSION_DATA_DIR"
    ok "已创建 session 数据目录: $KIMI_SESSION_DATA_DIR"
  fi
}

# ---------------- Build & Up ----------------
build_and_up() {
  section "获取镜像与启动"

  local _use_prebuilt _up
  ask_yn _use_prebuilt "使用预构建镜像（从 ghcr.io 拉取，无需本地编译）？${C_DIM} 选 N 则本地构建${C_RESET}" "y"

  if [ "$_use_prebuilt" = "true" ]; then
    info "拉取预构建镜像…"
    $COMPOSE_CMD --env-file "$ENV_FILE" -f "$COMPOSE_FILE" pull
    ok "镜像拉取完成"
  else
    info "开始本地构建镜像（首次构建可能需要较长时间）…"
    $COMPOSE_CMD --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build
    ok "镜像构建完成"
  fi

  ask_yn _up "现在执行 ${C_BOLD}$COMPOSE_CMD up -d${C_RESET}？" "y"
  if [ "$_up" = "true" ]; then
    $COMPOSE_CMD --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d
    ok "容器已启动"
  else
    info "跳过启动；稍后可手动执行: $COMPOSE_CMD up -d"
    return 0
  fi
}

# ---------------- Summary ----------------
print_summary() {
  local port token
  port="$(grep -E '^KIMI_WEB_PORT=' "$ENV_FILE" | cut -d= -f2)"
  token="$(grep -E '^KIMI_WEB_SESSION_TOKEN=' "$ENV_FILE" | cut -d= -f2)"

  section "部署完成 🎉"
  printf "  Web UI:    ${C_CYAN}http://localhost:%s${C_RESET}\n" "${port:-5494}"
  if [ -n "$token" ] && [ "$token" != "change-me" ]; then
    printf "  带 Token:  ${C_CYAN}http://localhost:%s/?token=%s${C_RESET}\n" "${port:-5494}" "$token"
  fi
  echo
  printf "  默认管理员账号: ${C_BOLD}admin / admin123${C_RESET} ${C_YELLOW}(请尽快通过 /admin 修改)${C_RESET}\n"
  echo
  printf "  常用命令:\n"
  printf "    查看日志:   ${C_DIM}%s logs -f gateway${C_RESET}\n" "$COMPOSE_CMD"
  printf "    停止服务:   ${C_DIM}%s down${C_RESET}\n" "$COMPOSE_CMD"
  printf "    重新部署:   ${C_DIM}./scripts/deploy.sh${C_RESET}\n"
  echo
}

# ---------------- Main ----------------
main() {
  banner
  check_prereqs
  onboard_env
  build_and_up
  print_summary
}

main "$@"
