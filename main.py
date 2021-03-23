import os
import mel_parser


def main():
    prog = mel_parser.parse('''
        input a input b  /* comment 1
        input c
        */
        c = a + b * (2 - 1) + 0  // comment 2
        output c + 1

        if a + 7 then b = 9 elif a + 1 then c = 2 else b = 8 end if
        
        int a = 7
        
        begin
        
        loop i = i + 1 end loop
        
        while red + a loop green = b end loop
        
        for a + 1, b + 2, c + 3 loop coffee = 1 end loop
        
        end
    ''')
    print(*prog.tree, sep=os.linesep)


if __name__ == "__main__":
    main()
