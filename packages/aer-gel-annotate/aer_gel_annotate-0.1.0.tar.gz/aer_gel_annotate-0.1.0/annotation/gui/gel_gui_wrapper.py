# annotation/gui/gel_gui_wrapper.py
import sys, os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QFileDialog, QSpinBox, QCheckBox,
    QGroupBox, QTextEdit, QScrollArea, QLineEdit, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from ..annotate import run_full_annotation, save_results_csv, save_results_json,load_results_json

from PyQt5.QtGui import QIcon
import importlib.resources as res
from pathlib import Path

def _icon_path(name: str) -> str:
    # Resolve packaged asset at runtime
    with res.as_file(res.files("annotation.assets") / name) as p:
        return str(p)

class GelAnnotationGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gel Well Detection and Annotation")
        self.setGeometry(80, 60, 1400, 800)

        self.image_path = None
        self.last_png = None
        self.last_result = None

        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout()

        # --- Top row: file path (left) + detection params (right) ---
        top_row = QHBoxLayout()

        # Left: file picker + path display
        file_box = QGroupBox("Image input path")
        file_lay = QHBoxLayout()
        self.path_display = QLineEdit()
        self.path_display.setPlaceholderText("Select an image...")
        self.path_display.setReadOnly(True)
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._select_file)
        file_lay.addWidget(self.path_display, 1)
        file_lay.addWidget(browse_btn, 0)
        file_box.setLayout(file_lay)



        # Right: detection parameters
        param_box = QGroupBox("Detection parameters")
        param_lay = QHBoxLayout()
        self.spin_comb_size = QSpinBox();
        self.spin_comb_size.setRange(1, 30);
        self.spin_comb_size.setValue(9)
        self.spin_comb_size.setPrefix("Comb Size: ")
        self.spin_combs_per_row = QSpinBox();
        self.spin_combs_per_row.setRange(1, 8);
        self.spin_combs_per_row.setValue(2)
        self.spin_combs_per_row.setPrefix("Combs/Row: ")
        self.chk_ladder = QCheckBox("Detect Ladder");
        self.chk_ladder.setChecked(True)
        self.chk_bands = QCheckBox("Detect PCR Bands");
        self.chk_bands.setChecked(True)
        run_btn = QPushButton("Run Detection");
        run_btn.clicked.connect(self._run_detection)
        for w in [self.spin_comb_size, self.spin_combs_per_row, self.chk_ladder, self.chk_bands, run_btn]:
            param_lay.addWidget(w)
        param_box.setLayout(param_lay)
        param_lay = QHBoxLayout()

        self.spin_comb_size = QSpinBox(); self.spin_comb_size.setRange(1, 30); self.spin_comb_size.setValue(9)
        self.spin_comb_size.setPrefix("Comb Size: ")

        self.spin_combs_per_row = QSpinBox(); self.spin_combs_per_row.setRange(1, 8); self.spin_combs_per_row.setValue(2)
        self.spin_combs_per_row.setPrefix("Combs/Row: ")

        self.chk_ladder = QCheckBox("Detect Ladder"); self.chk_ladder.setChecked(True)
        self.chk_bands = QCheckBox("Detect PCR Bands"); self.chk_bands.setChecked(True)

        run_btn = QPushButton("Run Detection")
        run_btn.clicked.connect(self._run_detection)

        for w in [self.spin_comb_size, self.spin_combs_per_row, self.chk_ladder, self.chk_bands, run_btn]:
            param_lay.addWidget(w)
        param_box.setLayout(param_lay)

        top_row.addWidget(file_box, 1)
        top_row.addWidget(param_box, 1)

        # Wrap top row in a fixed-height container so it doesn't eat vertical space
        top_container = QWidget()
        top_container.setLayout(top_row)
        top_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        top_container.setFixedHeight(90)  # adjust to taste (e.g., 90–120 px)
        root.addWidget(top_container)

        # --- Middle: splitter (left = manual/export, right = image) ---
        splitter = QSplitter(Qt.Horizontal)

        # Left panel
        left_panel = QWidget()
        left_lay = QVBoxLayout()

        manual_box = QGroupBox("Edit parameters")
        manual_lay = QVBoxLayout()
        self.txt_yes = QTextEdit(); self.txt_yes.setPlaceholderText("manual yes: e.g. 1, 5, 12")
        self.txt_no  = QTextEdit(); self.txt_no.setPlaceholderText("manual no: e.g. 2, 3, 8")
        manual_lay.addWidget(self.txt_yes)
        manual_lay.addWidget(self.txt_no)
        manual_box.setLayout(manual_lay)
        left_lay.addWidget(manual_box)
        # NEW: detected wells (read-only)
        detected_box = QGroupBox("Detected wells (read-only)")
        detected_lay = QVBoxLayout()
        self.txt_detected = QTextEdit()
        self.txt_detected.setReadOnly(True)
        self.txt_detected.setPlaceholderText("index: x, y")
        detected_lay.addWidget(self.txt_detected)
        detected_box.setLayout(detected_lay)
        left_lay.addWidget(detected_box)

        # NEW: ladder wells (read-only)
        ladder_box = QGroupBox("Ladder wells (read-only)")
        ladder_lay = QVBoxLayout()
        self.txt_ladder = QTextEdit()
        self.txt_ladder.setReadOnly(True)
        self.txt_ladder.setPlaceholderText("x, y")
        ladder_lay.addWidget(self.txt_ladder)
        ladder_box.setLayout(ladder_lay)
        left_lay.addWidget(ladder_box)

        # NEW: probable wells (editable)
        prob_box = QGroupBox("Probable wells (editable)")
        prob_lay = QVBoxLayout()
        self.txt_probable = QTextEdit()
        self.txt_probable.setPlaceholderText("x, y per line (e.g. 123.4, 567.8)")
        prob_lay.addWidget(self.txt_probable)

        apply_btn = QPushButton("Apply edits & re-run")
        apply_btn.clicked.connect(self._apply_edits_and_rerun)
        prob_lay.addWidget(apply_btn)

        prob_box.setLayout(prob_lay)
        left_lay.addWidget(prob_box)

        export_box = QGroupBox("Save / export")
        export_lay = QVBoxLayout()
        btn_load_json = QPushButton("Load JSON (results)")
        btn_load_json.clicked.connect(self._load_json)
        export_lay.addWidget(btn_load_json)

        btn_save_png = QPushButton("Save annotated PNG")
        btn_save_png.clicked.connect(self._save_png)

        btn_export_csv = QPushButton("Export CSV (results)")
        btn_export_csv.clicked.connect(self._export_csv)

        btn_export_json = QPushButton("Export JSON (results)")
        btn_export_json.clicked.connect(self._export_json)

        self.status = QLabel("")  # status / errors
        self.status.setWordWrap(True)

        for b in [btn_save_png, btn_export_csv, btn_export_json]:
            export_lay.addWidget(b)
        export_lay.addWidget(self.status)
        export_box.setLayout(export_lay)

        left_lay.addWidget(export_box)
        left_lay.addStretch(1)
        left_panel.setLayout(left_lay)

        splitter.addWidget(left_panel)

        # Right panel: image area (scrollable)
        self.image_label = QLabel("Image Area")
        self.image_label.setAlignment(Qt.AlignCenter)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.image_label)

        splitter.addWidget(scroll)
        splitter.setSizes([380, 1000])

        root.addWidget(splitter)
        # Make only the splitter grow/shrink vertically
        root.setStretch(0, 0)  # top_container fixed
        root.setStretch(1, 1)  # splitter expands
        self.setLayout(root)

    # ---------- Actions ----------
    def _select_file(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Select Gel Image", "", "Images (*.png *.jpg *.tif *.tiff)"
        )
        if not fname:
            return
        self.image_path = fname
        self.path_display.setText(fname)
        self.status.setText("")

    def _run_detection(self):
        if not self.image_path:
            self.status.setText("Please select an image first.")
            return
        try:
            manual_yes = self._parse_indices(self.txt_yes.toPlainText())
            manual_no = self._parse_indices(self.txt_no.toPlainText())

            png_path, result = run_full_annotation(
                image_path=self.image_path,
                comb_size=self.spin_comb_size.value(),
                combs_per_row=self.spin_combs_per_row.value(),
                ladder=self.chk_ladder.isChecked(),
                detect_bars=self.chk_bands.isChecked(),
                manual_yes=manual_yes, manual_no=manual_no,
                verbose=1
            )
            self.last_png = png_path
            self.last_result = result

            # show image
            pixmap = QPixmap(png_path)
            self.image_label.setPixmap(pixmap.scaled(1280, 900, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.status.setText(f"Detection complete. Saved preview: {os.path.basename(png_path)}")

            # populate text boxes
            self._fill_well_textboxes(result)

        except Exception as e:
            self.status.setText(f"Error: {e}")

    def _save_png(self):
        if not self.last_png:
            self.status.setText("Run detection first; no annotated image yet.")
            return
        # let user pick where to copy/save
        suggested = self._default_out_path("_annotated.png")
        fname, _ = QFileDialog.getSaveFileName(self, "Save annotated PNG", suggested, "PNG (*.png)")
        if not fname:
            return
        try:
            # Re-save/copy the already saved file
            from shutil import copyfile
            copyfile(self.last_png, fname)
            self.status.setText(f"Saved PNG: {fname}")
        except Exception as e:
            self.status.setText(f"Error saving PNG: {e}")

    def _export_csv(self):
        if not (self.image_path and self.last_result):
            self.status.setText("Run detection first; no results to export.")
            return
        suggested = self._default_out_path("_results.csv")
        fname, _ = QFileDialog.getSaveFileName(self, "Export CSV", suggested, "CSV (*.csv)")
        if not fname:
            return
        try:
            out = save_results_csv(self.image_path, self.last_result, fname)
            self.status.setText(f"CSV exported: {out}")
        except Exception as e:
            self.status.setText(f"Error exporting CSV: {e}")

    def _export_json(self):
        if not (self.image_path and self.last_result):
            self.status.setText("Run detection first; no results to export.")
            return
        suggested = self._default_out_path("_results.json")
        fname, _ = QFileDialog.getSaveFileName(self, "Export JSON", suggested, "JSON (*.json)")
        if not fname:
            return
        try:
            out = save_results_json(self.image_path, self.last_result, fname)
            self.status.setText(f"JSON exported: {out}")
        except Exception as e:
            self.status.setText(f"Error exporting JSON: {e}")

    # ---------- helpers ----------
    def _parse_indices(self, text):
        return [int(x.strip()) for x in text.split(",") if x.strip().isdigit()]

    def _default_out_path(self, suffix):
        root, _ = os.path.splitext(self.image_path or "output.png")
        return root + suffix

    def _fill_well_textboxes(self, result):
        # Detected wells (read-only)
        lines = [f"{w['index']}: {w['x']:.1f}, {w['y']:.1f}" for w in result.get("final_wells", [])]
        self.txt_detected.setPlainText("\n".join(lines))

        # Ladder wells (read-only)
        ladders = [f"{lw['x']:.1f}, {lw['y']:.1f}" for lw in result.get("ladder_wells", [])]
        self.txt_ladder.setPlainText("\n".join(ladders))

        # Probable wells (editable)
        prob = [f"{pw['x']:.1f}, {pw['y']:.1f}" for pw in result.get("probable_wells", [])]
        self.txt_probable.setPlainText("\n".join(prob))

    def _parse_xy_lines(self, text):
        coords = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            # accept "x,y" or "x  y" or "x\t y"
            for sep in [",", "\t", " "]:
                if sep in line:
                    parts = [p for p in line.replace("\t", " ").replace(",", " ").split(" ") if p]
                    if len(parts) >= 2:
                        try:
                            x = float(parts[0]);
                            y = float(parts[1])
                            coords.append((x, y))
                        except ValueError:
                            pass
                    break
        return coords

    def _apply_edits_and_rerun(self):
        if not self.image_path:
            self.status.setText("Please select an image first.")
            return
        try:
            manual_yes = self._parse_indices(self.txt_yes.toPlainText())
            manual_no = self._parse_indices(self.txt_no.toPlainText())
            user_probables = self._parse_xy_lines(self.txt_probable.toPlainText())

            png_path, result = run_full_annotation(
                image_path=self.image_path,
                comb_size=self.spin_comb_size.value(),
                combs_per_row=self.spin_combs_per_row.value(),
                ladder=self.chk_ladder.isChecked(),
                detect_bars=self.chk_bands.isChecked(),
                manual_yes=manual_yes, manual_no=manual_no,
                user_probable_wells=user_probables,  # <--- NEW
                verbose=1
            )
            self.last_png = png_path
            self.last_result = result

            pixmap = QPixmap(png_path)
            self.image_label.setPixmap(pixmap.scaled(1280, 900, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.status.setText("Re-run complete with edited probable wells.")
            self._fill_well_textboxes(result)
        except Exception as e:
            self.status.setText(f"Error re-running with edits: {e}")

    def _load_json(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Load results JSON", "", "JSON (*.json)"
        )
        if not fname:
            return
        try:
            result = load_results_json(fname)
            self.last_result = result
            # Fill the text boxes with stored coords
            self._fill_well_textboxes(result)
            self.status.setText(f"Loaded results from {os.path.basename(fname)}")
        except Exception as e:
            self.status.setText(f"Error loading JSON: {e}")

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(_icon_path("icon.ico")))
    gui = GelAnnotationGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
