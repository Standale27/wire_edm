from pygcode import Line
import argparse

parser = argparse.ArgumentParser(description="Indicate filenames for input and output files")
parser.add_argument("--infile", type=str, default=None, help="Specify an input file path")
parser.add_argument("--outfile", type=str, default=None, help="Specify an output file path")

args = parser.parse_args()

allowedCodes = ['O0027', 'G01', 'G02', 'G03', 'G40', 'G41', 'G42', 'M30', 'M31'] #EDM Specific Codes

class codeConverter():
    def __init__(self):   # Initializes class taking in an input and output file name. Appends the rows to self.lines
        if args.infile:
            self.ifn = args.infile     # input file name
        else:
            self.ifn = input("Please enter the input file path: ")
        if args.outfile:
            self.ofn = args.outfile   # output file name
        else:
            self.ofn = input("Please enter the output file path: ")
        
        
    def __enter__(self):
        self.infile = open(self.ifn, 'r')
        self.outfile = open(self.ofn, 'w')

        self.g91ct = 0
        self.g00ct = 0

        rows = self.infile.readlines()
        return rows

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.infile:
            self.infile.close()

    def writetofile(self, txt):     # Takes in a string and writes it to the next row in the output file
        self.outfile.write(txt)

    def appendbefore(self, line_txt, gcode, *chars):    # Append will insert a gcode before all other items in the row
        for char in chars:      # Iterate through all characters provided (X and Y)
            if line_txt.startswith(char):   # If the row starts with that character,
                line_txt = gcode + " " + line_txt   # append the provided gcode (G01) to the front of the row
        return line_txt
    
    def cuttercomp(self, line_txt):
        if line_txt.startswith('(R') or line_txt.startswith('(F'):
            line_txt = "G42 " + line_txt
        if line_txt.startswith('(L') or line_txt.startswith('(B'):
            line_txt = "G41 " + line_txt
        return line_txt

    def coderemoval(self, gcodelist, *codes):
        buffer = []
        for all in gcodelist.block.gcodes:
            for every in codes:
                if every not in str(all):
                    buffer.append(all)
        return buffer
    
    def writewithcomments(self, gcodelist, processedLine):
        def write_line(line, comment=None):
            if comment:
                self.writetofile('\n' + str(line))
                self.writetofile(f' ({comment})\n')
            else:
                self.writetofile(str(line) + '\n')

        if 'G91' in processedLine._text and self.g91ct == 0:
            codes = allowedCodes + ['G91']
            self.g91ct += 1
        elif 'G00' in processedLine._text and self.g00ct == 0:
            codes = allowedCodes + ['G00']
            self.g00ct += 1
        else:
            codes = allowedCodes

        for all in gcodelist:
            if any(code in str(all) for code in codes):
                comment = getattr(getattr(processedLine, 'comment', None), 'text', None)
                write_line(all, comment)

if __name__ == '__main__':
    c = codeConverter()

    with c as lines:
        for n, row in enumerate(lines):     # Iterate through all rows
            lines[n] = c.cuttercomp(lines[n])
            lines[n] = c.appendbefore(lines[n], 'G01', 'X', 'Y')    # If line begins with an X or a Y character, prefix the line with a G01
            lines[n] = c.appendbefore(lines[n], 'M31', 'G90 G94')
            lines[n] = c.appendbefore(lines[n], 'G40', 'M30')

            processedLine = Line(lines[n])

            processedLine.block.gcodes = c.coderemoval(processedLine, 'Z')  # Removes all Z moves
            if '%' in processedLine._text:      # Start/End '%' character processing
                c.writetofile(str(processedLine)+'\n')
            
            c.writewithcomments(processedLine.block.gcodes, processedLine)
    print("Done!")
