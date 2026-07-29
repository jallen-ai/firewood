#!/usr/bin/env python3
"""
Generate a print-quality QR code as inline SVG for the firewood flyer.

WHY SVG AND NOT PNG:
A QR code is pure black-and-white geometry. As SVG it stays razor sharp at any
print size and adds almost nothing to the file. A PNG would need to be very
large to print cleanly, and a blurry QR is a QR that does not scan.

WHY ERROR CORRECTION LEVEL H:
Level H can still be read with roughly 30% of the code damaged. These flyers are
going to sit on doors in Illinois weather and get handled with firewood gloves.
The extra density is worth it.

USAGE:
    python3 make-qr.py "https://USERNAME.github.io/firewood/"

Writes qr.svg and prints the inline <svg> snippet to paste into the flyer.
"""

import sys
import qrcode

QUIET_ZONE = 2   # modules of white margin. 4 is the spec, 2 is fine when the
                 # code sits inside its own white box on the page, and it lets
                 # the code render bigger in the same physical space.


def build(url: str) -> str:
    qr = qrcode.QRCode(
        version=None,                                   # auto-size to the data
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=1,
        border=QUIET_ZONE,
    )
    qr.add_data(url)
    qr.make(fit=True)

    matrix = qr.get_matrix()
    n = len(matrix)

    # Merge each run of horizontal dark modules into one rect. This cuts the
    # element count by roughly 60% versus one rect per module, which keeps the
    # flyer file small and makes it render faster in the browser's print engine.
    rects = []
    for y, row in enumerate(matrix):
        x = 0
        while x < n:
            if row[x]:
                run = x
                while run < n and row[run]:
                    run += 1
                rects.append(f'<rect x="{x}" y="{y}" width="{run - x}" height="1"/>')
                x = run
            else:
                x += 1

    return (
        f'<svg viewBox="0 0 {n} {n}" xmlns="http://www.w3.org/2000/svg" '
        f'shape-rendering="crispEdges" role="img" aria-label="QR code to order firewood">'
        f'<rect width="{n}" height="{n}" fill="#fff"/>'
        f'<g fill="#000">{"".join(rects)}</g></svg>'
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python3 make-qr.py <url>")

    target = sys.argv[1]
    svg = build(target)

    with open("qr.svg", "w") as fh:
        fh.write(svg)

    print(f"URL encoded : {target}")
    print(f"Modules     : {svg.split('viewBox=\"0 0 ')[1].split(' ')[0]}")
    print(f"Written     : qr.svg  ({len(svg):,} bytes)")
    print("\n--- paste this into the flyer, replacing the .qrbox contents ---\n")
    print(svg)
