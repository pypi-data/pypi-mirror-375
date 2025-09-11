import argparse, os
from .annotate import run_full_annotation

def parse_args():
    p = argparse.ArgumentParser(description="Run gel well annotation pipeline")
    p.add_argument("image_path", type=str)
    p.add_argument("--comb_size", type=int, default=9)
    p.add_argument("--combs_per_row", type=int, default=2)
    p.add_argument("--detect_bars", action="store_true")
    p.add_argument("--ladder", action="store_true")
    p.add_argument("--manual_yes", nargs="*", type=int, default=[])
    p.add_argument("--manual_no", nargs="*", type=int, default=[])
    p.add_argument("--threshold_method", type=str, default="local",
                   choices=["local", "multiotsu", "sauvola", "niblack"])
    p.add_argument("--gamma", type=float, default=1.0)
    p.add_argument("--target_width", type=int, default=700)
    p.add_argument("--verbose", type=int, choices=[0,1,2], default=1)
    p.add_argument("--output", type=str, default=None)
    return p.parse_args()

def main():
    args = parse_args()
    if not os.path.exists(args.image_path):
        print(f"Image file '{args.image_path}' does not exist.")
        return
    out = run_full_annotation(
        image_path=args.image_path,
        output_path=args.output,
        comb_size=args.comb_size,
        combs_per_row=args.combs_per_row,
        detect_bars=args.detect_bars,
        manual_yes=args.manual_yes,
        manual_no=args.manual_no,
        ladder=args.ladder,
        threshold_method=args.threshold_method,
        gamma=args.gamma,
        target_width=args.target_width,
        verbose=args.verbose
    )
    print(f"Saved: {out}")

if __name__ == "__main__":
    main()
