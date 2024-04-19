import svgwrite
import argparse
import re

# Constants
top_unit_size_mm = 42  # The top size of the grid unit in mm (for spacing)
base_unit_size_mm = 37.1  # The base size of the grid unit in mm (for drawing)
corner_radius_mm = 1.6  # Radius of the rounded corners in mm
mm_per_inch = 25.4  # Millimeters per inch
dpi = 96  # DPI (standard for many systems)
hairline_stroke_mm = .01  # Hairline stroke width in mm for laser cutting


def mm_to_px(mm):
    """Convert millimeters to pixels using the specified DPI."""
    return mm * (dpi / mm_per_inch)


def fraction_to_float(fraction_str):
    """Convert fraction strings to floats."""
    if ' ' in fraction_str:  # Check if it contains a space indicating a fraction
        whole, fraction = fraction_str.split(' ')
        numerator, denominator = map(int, fraction.split('/'))
        return float(whole) + (numerator / denominator)
    else:
        return float(fraction_str)


def convert_to_inches(dimensions_str):
    """Convert dimensions with units to inches."""
    value, unit = re.match(r'([\d./\s]+)(\w*)',
                           dimensions_str).groups()
    value_in_inches = fraction_to_float(value)
    if unit.lower() == 'mm':
        value_in_inches /= mm_per_inch
    return value_in_inches


def create_gridfinity_baseplate_svg(filename, top_unit_size_px, base_unit_size_px, corner_radius_px,
                                    drawer_size_inch=None):
    drawer_width_inch, drawer_height_inch = drawer_size_inch
    drawer_width_px = mm_to_px(drawer_width_inch * mm_per_inch)
    drawer_height_px = mm_to_px(drawer_height_inch * mm_per_inch)

    cols = max(int(drawer_width_px // top_unit_size_px), 1)
    rows = max(int(drawer_height_px // top_unit_size_px), 1)

    # Calculate the drawing width and height including dynamic border
    width_px = drawer_width_px
    height_px = drawer_height_px
    start_x_px = (width_px - (cols * top_unit_size_px)) / 2
    start_y_px = (height_px - (rows * top_unit_size_px)) / 2

    print(
        f"Drawer mode: Fitting {cols} columns and {rows} rows within a {drawer_width_inch} inch x {drawer_height_inch} inch drawer.")

    # Create SVG drawing with explicit size in pixels
    dwg = svgwrite.Drawing(filename, size=(f"{width_px}px", f"{height_px}px"), profile='tiny')

    # Draw the enclosing border
    dwg.add(dwg.rect(insert=(0, 0), size=(f"{width_px}px", f"{height_px}px"), rx=f"{corner_radius_px}px",
                     ry=f"{corner_radius_px}px", stroke="black", fill="none",
                     stroke_width=f"{mm_to_px(hairline_stroke_mm)}px"))

    # Draw the grid with rounded corners inside the border
    for x in range(cols):
        for y in range(rows):
            x_pos_px = start_x_px + x * top_unit_size_px + (top_unit_size_px - base_unit_size_px) / 2
            y_pos_px = start_y_px + y * top_unit_size_px + (top_unit_size_px - base_unit_size_px) / 2
            dwg.add(dwg.rect(insert=(f"{x_pos_px}px", f"{y_pos_px}px"),
                             size=(f"{base_unit_size_px}px", f"{base_unit_size_px}px"), rx=f"{corner_radius_px}px",
                             ry=f"{corner_radius_px}px", stroke="black", fill="none",
                             stroke_width=f"{mm_to_px(hairline_stroke_mm)}px"))

    dwg.save()


def main():
    parser = argparse.ArgumentParser(description="Create a SVG for a Gridfinity baseplate.")
    parser.add_argument("--drawer_width", type=convert_to_inches,
                        help="Width of the drawer in inches. Supports fractions and units like 'mm'.")
    parser.add_argument("--drawer_height", type=convert_to_inches,
                        help="Height of the drawer in inches. Supports fractions and units like 'mm'.")
    parser.add_argument("--output", type=str, default="gridfinity_baseplate.svg",
                        help="Output filename for the SVG file.")

    args = parser.parse_args()

    if args.drawer_width and args.drawer_height:
        create_gridfinity_baseplate_svg(args.output, mm_to_px(top_unit_size_mm),
                                        mm_to_px(base_unit_size_mm),
                                        mm_to_px(corner_radius_mm),
                                        drawer_size_inch=(args.drawer_width, args.drawer_height))
    else:
        print("Please provide drawer dimensions in inches.")
        exit(1)


if __name__ == "__main__":
    main()
