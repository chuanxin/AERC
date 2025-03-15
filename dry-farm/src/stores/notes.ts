import { defineStore } from "pinia";
import { ref } from "vue";

interface Note {
  id: string;
  content: string;
  timestamp: Date;
}

export const useNotesStore = defineStore("notes", {
  state: () => ({
    notes: ref<Note[]>([]),
  }),
  actions: {
    addNote(note: Note) {
      this.notes.push(note);
    },
    removeNote(index: number) {
      this.notes.splice(index, 1);
    },
  },
});
