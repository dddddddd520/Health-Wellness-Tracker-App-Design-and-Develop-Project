from cairosvg import svg2png
import os

def convert_svg_to_png(svg_path, png_path):
    with open(svg_path, 'rb') as svg_file:
        svg_content = svg_file.read()
        svg2png(bytestring=svg_content, write_to=png_path, output_width=48, output_height=48)

def main():
    static_dir = 'static/images'
    icons = ['google-icon', 'microsoft-icon', 'apple-icon']
    
    for icon in icons:
        svg_path = os.path.join(static_dir, f'{icon}.svg')
        png_path = os.path.join(static_dir, f'{icon}.png')
        convert_svg_to_png(svg_path, png_path)
        print(f'Converted {icon}.svg to {icon}.png')

if __name__ == '__main__':
    main() 