#!/usr/bin/env python3
"""DIO Explorer TUI — navegue trilhas com /trilha, /desafio e /certificado."""

import curses
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import controller as ctrl_module
import view
from model import ProgressRepository, TrilhaRepository
from service import CertificateService, ChallengeService, ProgressService, TrilhaService

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "trilhas_dio.json")
PROGRESS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "progress.json")
CERTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "certificados_emitidos")


def _rebuild_wins(stdscr, h: int, w: int):
    stdscr.clear()
    stdscr.refresh()
    return view.make_wins(h, w)


def main(stdscr) -> None:
    curses.curs_set(0)
    view.init_colors()
    stdscr.keypad(True)

    repo = TrilhaRepository(DATA_PATH)
    service = TrilhaService(repo)
    progress_repo = ProgressRepository(PROGRESS_PATH)
    progress_service = ProgressService(progress_repo)
    challenge_service = ChallengeService()
    certificate_service = CertificateService(CERTS_DIR)
    ctrl = ctrl_module.Controller(service, progress_service, challenge_service, certificate_service)

    h, w = stdscr.getmaxyx()
    list_win, detail_win, cmd_win, main_h, list_w, detail_w = view.make_wins(h, w)

    stdscr.refresh()
    view.redraw(stdscr, list_win, detail_win, cmd_win, main_h, list_w, detail_w, ctrl.state)

    while True:
        key = stdscr.getch()

        # recreate windows on terminal resize
        new_h, new_w = stdscr.getmaxyx()
        if new_h != h or new_w != w:
            h, w = new_h, new_w
            list_win, detail_win, cmd_win, main_h, list_w, detail_w = view.make_wins(h, w)
            stdscr.clear()
            stdscr.refresh()

        # fullscreen detail on Enter
        if not ctrl.state.in_cmd_mode and key in (ord("\n"), curses.KEY_ENTER):
            trilha_atual = ctrl.current_trilha()
            if trilha_atual:
                tid = trilha_atual["id"]
                in_progress = tid in ctrl.state.in_progress_ids
                completed = tid in ctrl.state.completed_ids

                action = view.show_fullscreen(
                    stdscr, trilha_atual, in_progress=in_progress, completed=completed
                )

                if action == view.FS_TOGGLE:
                    ctrl.toggle_progress()
                elif action == view.FS_CHALLENGE:
                    challenge_text = ctrl.generate_challenge(trilha_atual)
                    concluded = view.show_challenge(stdscr, trilha_atual, challenge_text)
                    if concluded:
                        ctrl.complete_current(trilha_atual)
                elif action == view.FS_CERTIFICATE:
                    if ctrl.has_certificate(trilha_atual["id"]):
                        ctrl.state.message = "🔖 Certificado já emitido — exibindo cópia salva."
                        cert_lines, _ = ctrl.get_certificate(trilha_atual, "")
                    else:
                        username = view.ask_username(stdscr)
                        if not username:
                            cert_lines = []
                        else:
                            cert_lines, _ = ctrl.get_certificate(trilha_atual, username)
                    if cert_lines:
                        view.show_certificate(stdscr, cert_lines)

                list_win, detail_win, cmd_win, main_h, list_w, detail_w = _rebuild_wins(
                    stdscr, h, w
                )
        else:
            if not ctrl.handle_key(key, main_h - 2):
                break

        view.redraw(stdscr, list_win, detail_win, cmd_win, main_h, list_w, detail_w, ctrl.state)


def run() -> None:
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()
