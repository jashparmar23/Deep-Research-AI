import subprocess
import re
from typing import Optional


class GGUFModel:
    def __init__(
        self,
        model_path: str,
        llama_cli_path: str,
        threads: int = 6,
        max_tokens: int = 256,
        temperature: float = 0.7,
        timeout: int = 600,
    ):
        self.model_path = model_path
        self.llama_cli_path = llama_cli_path
        self.threads = threads
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

    # ------------------------------------------------------------------ #
    #  BASIC GENERATION (single chunk)                                   #
    # ------------------------------------------------------------------ #
    def generate_text(self, prompt: str, timeout: Optional[int] = None) -> str:
        """Run llama-cli once and return raw output (one chunk)."""
        if timeout is None:
            timeout = self.timeout

        cmd = [
            self.llama_cli_path,
            "-m", self.model_path,
            "-no-cnv",
            "-p", prompt,
            "-n", str(self.max_tokens),
            "-t", str(self.threads),
            "--temp", str(self.temperature),
            "--simple-io",
            "--no-mmap",
        ]

        print("Running command:", " ".join(f'"{c}"' if " " in c else c for c in cmd))

        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = proc.communicate(timeout=timeout)

            if proc.returncode != 0:
                print(f"llama-cli error:\n{stderr}")
                return ""

            output = stdout.strip()
            # Remove any token-formatting artefacts
            output = re.sub(r"\[/?INST\]", "", output)
            output = re.sub(r"<[^>]+>", "", output)

            # In case model echoes the prompt, drop it
            if prompt in output:
                output = output.split(prompt, 1)[-1].strip()

            return output
        except subprocess.TimeoutExpired:
            proc.kill()
            print(f"Generation timed-out after {timeout} s")
            return ""

    # ------------------------------------------------------------------ #
    #  ITERATIVE GENERATION (multi-chunk, merged)                        #
    # ------------------------------------------------------------------ #
    def iterative_generate(
        self,
        prompt: str,
        max_total_tokens: int = 1024,
        chunk_size: int = 256,
        timeout: Optional[int] = None,
    ) -> str:
        """
        Keep calling llama-cli in chunks until `max_total_tokens`
        is reached or generation stalls.
        """
        if timeout is None:
            timeout = self.timeout

        merged = ""
        tokens_left = max_total_tokens
        current_prompt = prompt

        while tokens_left > 0:
            self.max_tokens = min(chunk_size, tokens_left)
            chunk = self.generate_text(current_prompt, timeout=timeout)

            # Model returned nothing → stop
            if not chunk.strip():
                break

            merged += chunk
            current_prompt += chunk
            tokens_left -= self.max_tokens

        return merged.strip()

    # ------------------------------------------------------------------ #
    #  ENHANCED GENERATION (clean summary – NEW IMPLEMENTATION)          #
    # ------------------------------------------------------------------ #
    def enhanced_generation(
        self,
        original_prompt: str,
        initial_output: str,
        web_data: str,
        max_total_tokens: int = 1024,
        chunk_size: int = 256,
        timeout: Optional[int] = None,
    ) -> str:
        """
        Generate a SINGLE merged summary that contains only facts found in `web_data`.
        No prompt scaffolding or model reasoning should appear in the final answer.
        """
        if timeout is None:
            timeout = self.timeout

        # -- Clean, self-contained prompt --------------------------------
        enhanced_prompt = (
            f"{original_prompt}\n\n"
            f"=== Source Text Start ===\n{web_data}\n=== Source Text End ===\n\n"
            "Write a concise, structured summary **using ONLY facts that appear "
            "verbatim in the Source Text**. "
            "Do NOT invent, guess, or paraphrase unseen information. "
            "If the Source Text lacks enough information, output exactly: "
            "\"Not enough explicit information found.\""
        )

        # -- Generate (handles chunking & merges) ------------------------
        merged = self.iterative_generate(
            enhanced_prompt,
            max_total_tokens=max_total_tokens,
            chunk_size=chunk_size,
            timeout=timeout,
        )

        # -- Final clean-up: strip any echoed prompt / markers -----------
        merged = re.sub(
            r"=== Source Text Start ===.*?=== Source Text End ===",
            "",
            merged,
            flags=re.S,
        ).strip()

        return merged
