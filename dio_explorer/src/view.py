"""View layer — all curses rendering. Receives data as parameters; holds no app state."""

import curses

from controller import AppState
from model import Trilha

# ──────────────────────────────────────────────
# Color pair constants
# ──────────────────────────────────────────────
C_NORMAL = 1
C_HEADER = 2
C_SELECTED = 3
C_TITLE = 4
C_BADGE = 5
C_DIM = 6
C_PROMO = 7
C_CMD = 8


def init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(C_NORMAL, curses.COLOR_WHITE, -1)
    curses.init_pair(C_HEADER, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(C_SELECTED, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(C_TITLE, curses.COLOR_CYAN, -1)
    curses.init_pair(C_BADGE, curses.COLOR_MAGENTA, -1)
    curses.init_pair(C_DIM, curses.COLOR_WHITE, -1)
    curses.init_pair(C_PROMO, curses.COLOR_GREEN, -1)
    curses.init_pair(C_CMD, curses.COLOR_YELLOW, -1)


# ──────────────────────────────────────────────
# Drawing helpers
# ──────────────────────────────────────────────
def safe_addstr(win, y: int, x: int, text: str, attr: int = 0) -> None:
    h, w = win.getmaxyx()
    if y < 0 or y >= h or x < 0 or x >= w:
        return
    max_len = w - x - 1
    if max_len <= 0:
        return
    try:
        win.addstr(y, x, text[:max_len], attr)
    except curses.error:
        pass


def draw_hline(win, y: int, char: str = "─", attr: int = 0) -> None:
    _, w = win.getmaxyx()
    safe_addstr(win, y, 0, char * (w - 1), attr)


# ──────────────────────────────────────────────
# Left panel — trilha list
# ──────────────────────────────────────────────
def draw_list(win, trilhas: list[Trilha], selected: int, offset: int) -> None:
    h, w = win.getmaxyx()
    win.erase()
    header_attr = curses.color_pair(C_HEADER) | curses.A_BOLD
    safe_addstr(win, 0, 0, " TRILHAS DIO ".center(w - 1), header_attr)
    visible = h - 2
    for i, t in enumerate(trilhas[offset : offset + visible]):
        idx = offset + i
        row = i + 1
        level_icon = {"Iniciante": "●", "Intermediário": "◆", "Avançado": "★"}.get(t["level"], "·")
        text = f" {level_icon} {t['name']}"
        if idx == selected:
            sel_attr = curses.color_pair(C_SELECTED) | curses.A_BOLD
            safe_addstr(win, row, 0, text.ljust(w - 1), sel_attr)
        else:
            safe_addstr(win, row, 0, text.ljust(w - 1), curses.color_pair(C_NORMAL))
    counter = f" {selected + 1}/{len(trilhas)} ".ljust(w - 1)
    safe_addstr(win, h - 1, 0, counter, curses.color_pair(C_DIM) | curses.A_DIM)
    win.noutrefresh()


# ──────────────────────────────────────────────
# Right panel — trilha detail
# ──────────────────────────────────────────────
def draw_detail(win, trilha: Trilha | None) -> None:
    h, w = win.getmaxyx()
    win.erase()
    safe_addstr(win, 0, 0, " DETALHES ".center(w - 1), curses.color_pair(C_HEADER) | curses.A_BOLD)

    if not trilha:
        safe_addstr(win, 2, 2, "Nenhuma trilha encontrada.", curses.color_pair(C_DIM))
        win.noutrefresh()
        return

    row = 1

    def line(text: str = "", attr: int = 0) -> None:
        nonlocal row
        if row < h - 1:
            safe_addstr(win, row, 1, text, attr)
            row += 1

    promo = trilha["promotions"]
    lifetime = "Sim ♾️" if trilha["lifetime"] else "Não"
    discount = promo["discount"]
    has_promo = discount != "0%"

    line()
    line(f"📚 {trilha['name']}", curses.color_pair(C_TITLE) | curses.A_BOLD)
    line()
    line(f"  Tecnologia : {trilha['technology']}", curses.color_pair(C_NORMAL))
    line(f"  Nível      : {trilha['level']}", curses.color_pair(C_NORMAL))
    line(f"  Módulos    : {trilha['modules']}", curses.color_pair(C_NORMAL))
    line(f"  XP Total   : {trilha['total_xp']} XP", curses.color_pair(C_NORMAL))
    line(f"  Vitalício  : {lifetime}", curses.color_pair(C_NORMAL))
    line()
    draw_hline(win, row, "·", curses.color_pair(C_DIM) | curses.A_DIM)
    row += 1
    line()
    line("  🏅 Badges:", curses.color_pair(C_BADGE) | curses.A_BOLD)
    for badge in trilha["available_badges"]:
        line(f"     🎖️  {badge}", curses.color_pair(C_BADGE))
    line()
    draw_hline(win, row, "·", curses.color_pair(C_DIM) | curses.A_DIM)
    row += 1
    line()
    line("  📺 Lives:", curses.color_pair(C_NORMAL) | curses.A_BOLD)
    for live in trilha["lives"]:
        line(f"     • {live['title']}", curses.color_pair(C_NORMAL))
        line(f"       {live['date']}", curses.color_pair(C_DIM) | curses.A_DIM)
    line()
    draw_hline(win, row, "·", curses.color_pair(C_DIM) | curses.A_DIM)
    row += 1
    line()
    if has_promo:
        promo_attr = curses.color_pair(C_PROMO) | curses.A_BOLD
        line(f"  🏷️  Promoção: {discount} off — até {promo['valid_until']}", promo_attr)
        line(f"     {promo['description']}", curses.color_pair(C_PROMO))
    else:
        line("  Sem promoção ativa.", curses.color_pair(C_DIM) | curses.A_DIM)

    win.noutrefresh()


# ──────────────────────────────────────────────
# Command bar
# ──────────────────────────────────────────────
def draw_cmdbar(win, prompt: str, cmd_input: str, message: str) -> None:
    h, w = win.getmaxyx()
    win.erase()
    draw_hline(win, 0, "─", curses.color_pair(C_DIM) | curses.A_DIM)
    help_text = " /trilha [filtro]  ↑↓ navegar  Enter detalhe  Esc limpar  q sair"
    safe_addstr(win, 1, 0, help_text[: w - 1], curses.color_pair(C_DIM) | curses.A_DIM)
    input_line = f"{prompt}{cmd_input}"
    if message:
        safe_addstr(win, 2, 0, message[: w - 1], curses.color_pair(C_CMD) | curses.A_BOLD)
    else:
        safe_addstr(win, 2, 0, input_line[: w - 1], curses.color_pair(C_CMD) | curses.A_BOLD)
    win.noutrefresh()


# ──────────────────────────────────────────────
# Fullscreen detail overlay
# ──────────────────────────────────────────────
def show_fullscreen(stdscr, trilha: Trilha) -> None:
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    lines = []
    promo = trilha["promotions"]
    has_promo = promo["discount"] != "0%"
    lines.append(("", 0))
    lines.append((f"  📚 {trilha['name']}", curses.color_pair(C_TITLE) | curses.A_BOLD))
    lines.append(("", 0))
    lines.append((f"  Tecnologia : {trilha['technology']}", 0))
    lines.append((f"  Nível      : {trilha['level']}", 0))
    lines.append((f"  Módulos    : {trilha['modules']}", 0))
    lines.append((f"  XP Total   : {trilha['total_xp']} XP", 0))
    lines.append((f"  Vitalício  : {'Sim' if trilha['lifetime'] else 'Não'}", 0))
    lines.append(("", 0))
    lines.append(("  🏅 Badges:", curses.color_pair(C_BADGE) | curses.A_BOLD))
    for b in trilha["available_badges"]:
        lines.append((f"     🎖️  {b}", curses.color_pair(C_BADGE)))
    lines.append(("", 0))
    lines.append(("  📺 Lives:", curses.A_BOLD))
    for live in trilha["lives"]:
        lines.append((f"     • {live['title']} — {live['date']}", 0))
    lines.append(("", 0))
    lines.append(("  🏷️  Promoção:", curses.color_pair(C_PROMO) | curses.A_BOLD))
    if has_promo:
        promo_line = f"     {promo['discount']} off até {promo['valid_until']}"
        lines.append((promo_line, curses.color_pair(C_PROMO)))
        lines.append((f"     {promo['description']}", curses.color_pair(C_PROMO)))
    else:
        lines.append(("     Sem promoção ativa.", curses.color_pair(C_DIM) | curses.A_DIM))
    lines.append(("", 0))
    back_attr = curses.color_pair(C_DIM) | curses.A_DIM
    lines.append(("  [ pressione qualquer tecla para voltar ]", back_attr))

    offset = 0
    while True:
        stdscr.erase()
        header_attr = curses.color_pair(C_HEADER) | curses.A_BOLD
        safe_addstr(stdscr, 0, 0, " DETALHE COMPLETO ".center(w - 1), header_attr)
        for i, (text, attr) in enumerate(lines[offset:]):
            row = i + 1
            if row >= h - 1:
                break
            safe_addstr(stdscr, row, 0, text, attr)
        stdscr.refresh()
        key = stdscr.getch()
        if key in (ord("q"), 27, ord("\n"), curses.KEY_BACKSPACE):
            break
        elif key == curses.KEY_DOWN and offset < len(lines) - (h - 2):
            offset += 1
        elif key == curses.KEY_UP and offset > 0:
            offset -= 1


# ──────────────────────────────────────────────
# Window layout
# ──────────────────────────────────────────────
def make_wins(h: int, w: int) -> tuple:
    list_w = max(30, w // 2)
    detail_w = w - list_w
    cmd_h = 4
    main_h = h - cmd_h
    list_win = curses.newwin(main_h, list_w, 0, 0)
    detail_win = curses.newwin(main_h, detail_w, 0, list_w)
    cmd_win = curses.newwin(cmd_h, w, main_h, 0)
    return list_win, detail_win, cmd_win, main_h, list_w, detail_w


# ──────────────────────────────────────────────
# Full redraw
# ──────────────────────────────────────────────
def redraw(  # noqa: PLR0913
    stdscr,
    list_win,
    detail_win,
    cmd_win,
    main_h,
    list_w,
    detail_w,
    state: AppState,
) -> None:
    trilha_atual = state.visible_trilhas[state.selected] if state.visible_trilhas else None
    draw_list(list_win, state.visible_trilhas, state.selected, state.list_offset)
    draw_detail(detail_win, trilha_atual)
    draw_cmdbar(
        cmd_win,
        state.prompt,
        state.cmd_input if state.in_cmd_mode else "",
        state.message,
    )
    if state.in_cmd_mode:
        curses.curs_set(1)
        cmd_win.move(2, len(state.prompt) + len(state.cmd_input))
    else:
        curses.curs_set(0)
    stdscr.noutrefresh()
    curses.doupdate()
