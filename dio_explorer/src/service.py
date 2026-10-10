"""Service layer — business logic for trilha operations."""

import textwrap
from dataclasses import dataclass

from model import ProgressRepository, Trilha, TrilhaRepository

# ──────────────────────────────────────────────
# Challenge templates per level
# ──────────────────────────────────────────────
_CHALLENGE_TEMPLATES: dict[str, str] = {
    "Iniciante": textwrap.dedent(
        """\
        📋 Descrição
        Escreva um programa na tecnologia {technology} que leia uma lista de números
        inteiros fornecidos pelo usuário e exiba: o maior valor, o menor valor e a
        média aritmética dos elementos.

        📥 Entrada
        Uma sequência de números inteiros separados por espaço (ex: 3 7 1 9 4).

        📤 Saída
        Maior: <valor>
        Menor: <valor>
        Média: <valor>

        💡 Dica
        Percorra a lista uma única vez e mantenha variáveis auxiliares para
        acompanhar o maior, o menor e a soma acumulada.
        """
    ),
    "Intermediário": textwrap.dedent(
        """\
        📋 Descrição
        Usando {technology}, implemente uma função que receba um texto e retorne
        um dicionário com a frequência de cada palavra (case-insensitive),
        ignorando pontuação. Em seguida, exiba as 3 palavras mais frequentes.

        📥 Entrada
        Uma string de texto com várias palavras (ex: "O rato roeu a roupa do rei").

        📤 Saída
        Um dicionário ordenado pelas 3 palavras mais frequentes e suas contagens.

        💡 Dica
        Normalize o texto removendo pontuação antes de dividir em palavras,
        depois ordene o dicionário resultante pelo valor decrescente.
        """
    ),
    "Avançado": textwrap.dedent(
        """\
        📋 Descrição
        Em {technology}, implemente um cache LRU (Least Recently Used) com
        capacidade configurável. O cache deve suportar as operações get(key)
        e put(key, value) em tempo O(1) para ambas.

        📥 Entrada
        Sequência de operações: put(1, "a"), get(1), put(2, "b"), get(3)...
        A capacidade máxima é fornecida na inicialização.

        📤 Saída
        O resultado de cada operação get (valor ou None se não encontrado).

        💡 Dica
        Combine um dicionário (hash map) com uma lista duplamente ligada para
        garantir O(1) em ambas as operações.
        """
    ),
}


@dataclass
class SearchResult:
    trilhas: list[Trilha]
    message: str
    found: bool


class TrilhaService:
    def __init__(self, repo: TrilhaRepository) -> None:
        self._repo = repo

    def all(self) -> list[Trilha]:
        return self._repo.all()

    def search(self, query: str) -> SearchResult:
        q = query.lower().strip()
        if not q:
            return SearchResult(
                trilhas=self._repo.all(),
                message="",
                found=True,
            )
        results = [
            t for t in self._repo.all() if q in t["name"].lower() or q in t["technology"].lower()
        ]
        if results:
            return SearchResult(
                trilhas=results,
                message=f"✔ {len(results)} trilha(s) encontrada(s).",
                found=True,
            )
        return SearchResult(
            trilhas=self._repo.all(),
            message="✘ Nenhuma trilha encontrada. Mostrando todas.",
            found=False,
        )


class ProgressService:
    def __init__(self, repo: ProgressRepository) -> None:
        self._repo = repo

    def is_in_progress(self, trilha_id: int) -> bool:
        return self._repo.is_in_progress(trilha_id)

    def all_ids(self) -> set[int]:
        return self._repo.all_ids()

    def toggle(self, trilha_id: int) -> str:
        """Start or stop a trilha. Returns a feedback message."""
        if self._repo.is_completed(trilha_id):
            return "✔ Trilha já concluída."
        if self._repo.is_in_progress(trilha_id):
            self._repo.remove(trilha_id)
            return "✘ Trilha removida do progresso."
        self._repo.add(trilha_id)
        return "✔ Trilha marcada como em andamento!"

    def complete(self, trilha_id: int) -> str:
        """Mark a trilha as completed (irreversible). Returns a feedback message."""
        self._repo.complete(trilha_id)
        return "🏆 Trilha concluída! Parabéns!"

    def all_completed_ids(self) -> set[int]:
        return self._repo.all_completed_ids()


class ChallengeService:
    def generate(self, trilha: Trilha) -> str:
        """Generate a challenge text for the given trilha based on its level."""
        level = trilha["level"]
        technology = trilha["technology"]
        template = _CHALLENGE_TEMPLATES.get(level, _CHALLENGE_TEMPLATES["Iniciante"])
        return template.format(technology=technology)
