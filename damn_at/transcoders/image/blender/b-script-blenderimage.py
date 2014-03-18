import bpy

import sys
import argparse


def main():
    # Drop everything before '--'
    args = sys.argv[sys.argv.index('--')+1:]

    parser = argparse.ArgumentParser(description='Render.')
    parser.add_argument('subname')
    parser.add_argument('file_path')
    
    args = parser.parse_args(args)
    
    if args.subname in bpy.data.images:
        image = bpy.data.images[args.subname]
        image.save_render(args.file_path)

if __name__ == '__main__':
    main()
