"""Q&A behavior mixin for code-image tab."""


class CodeImageQAMixin:
    """Handle optional Q&A data entry and AI answer generation."""

    def _supports_qa_content(self):
        return False

    def _refresh_qa_list(self):
        if self.qa_tree is None:
            return
        for child in self.qa_tree.get_children():
            self.qa_tree.delete(child)

        for idx, qa in enumerate(self.qa_items, 1):
            question = (qa.get("pertanyaan") or qa.get("q") or "").strip()
            answer = (qa.get("jawaban") or qa.get("a") or "").strip()
            self.qa_tree.insert("", "end", iid=str(idx - 1), values=(question, answer))

    def _serialize_qa_items(self):
        lines = []
        for idx, qa in enumerate(self.qa_items, 1):
            question = (qa.get("pertanyaan") or qa.get("q") or "").strip()
            answer = (qa.get("jawaban") or qa.get("a") or "").strip()
            if question:
                lines.append(f"{idx}. Q: {question}")
            if answer:
                lines.append(f"   A: {answer}")
        return "\n".join(lines)

    def _on_qa_select(self, _event=None):
        if self.qa_tree is None:
            return
        selected = self.qa_tree.selection()
        if not selected:
            self.qa_question_var.set("")
            self.qa_answer_var.set("")
            return
        try:
            idx = int(selected[0])
        except (ValueError, TypeError):
            return
        if idx < 0 or idx >= len(self.qa_items):
            return
        qa = self.qa_items[idx]
        self.qa_question_var.set((qa.get("pertanyaan") or qa.get("q") or "").strip())
        self.qa_answer_var.set((qa.get("jawaban") or qa.get("a") or "").strip())

    def _add_qa_item(self):
        if not self._supports_qa_content():
            return
        question = self.qa_question_var.get().strip()
        answer = self.qa_answer_var.get().strip()
        if not question and not answer:
            self.show_warning("Validasi", "Isi pertanyaan atau jawaban terlebih dahulu.")
            return
        self.qa_items.append({"pertanyaan": question, "jawaban": answer})
        self._refresh_qa_list()
        self.qa_question_var.set("")
        self.qa_answer_var.set("")

    def _update_qa_item(self):
        if not self._supports_qa_content() or self.qa_tree is None:
            return
        selected = self.qa_tree.selection()
        if not selected:
            self.show_warning("Validasi", "Pilih Q and A terlebih dahulu.")
            return
        try:
            idx = int(selected[0])
        except (ValueError, TypeError):
            return
        if idx < 0 or idx >= len(self.qa_items):
            return
        self.qa_items[idx] = {
            "pertanyaan": self.qa_question_var.get().strip(),
            "jawaban": self.qa_answer_var.get().strip(),
        }
        self._refresh_qa_list()
        self.qa_tree.selection_set(str(idx))

    def _remove_qa_item(self):
        if not self._supports_qa_content() or self.qa_tree is None:
            return
        selected = self.qa_tree.selection()
        if not selected:
            self.show_warning("Validasi", "Pilih Q and A terlebih dahulu.")
            return
        try:
            idx = int(selected[0])
        except (ValueError, TypeError):
            return
        if idx < 0 or idx >= len(self.qa_items):
            return
        self.qa_items.pop(idx)
        self._refresh_qa_list()
        self.qa_question_var.set("")
        self.qa_answer_var.set("")

    def _generate_qa_answer(self):
        if not self._supports_qa_content():
            return
        question = self.qa_question_var.get().strip()
        if not question:
            self.show_warning("Validasi", "Isi pertanyaan terlebih dahulu.")
            return
        modul_text = self.app.cover_tab.get_modul_text()
        answer, err = self.app.analysis_service.answer_question(question, modul_text)
        if err:
            self.show_error("AI Error", err)
            return
        self.qa_answer_var.set(answer or "")
        self.status_var.set("Jawaban AI berhasil diisi.")
