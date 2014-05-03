import bpy

import os, sys
import argparse
from string import Template


def main():
    # Drop everything before '--'
    args = sys.argv[sys.argv.index('--')+1:]

    parser = argparse.ArgumentParser(description='Render.')
    parser.add_argument('mimetype')
    parser.add_argument('subname')
    parser.add_argument('destination')

    args = parser.parse_args(args)
    
    text = bpy.data.texts[args.subname]
    
    if not os.path.exists(os.path.dirname(args.destination)):
        os.makedirs(os.path.dirname(args.destination))
        
    data = text.as_string()
    if data.strip() == '':
        data = 'application/x-blender.text\n EMPTY'
    print('-'*70)
    print(data)
    print('-'*70)

    with open(args.destination, 'wb') as file:
        file.write(bytes(data, 'UTF-8'))
        file.flush()
        
    
if __name__ == '__main__':
    main()
