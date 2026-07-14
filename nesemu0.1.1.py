#!/usr/bin/env python3.14

# ==========================================
# ByChatGPT NES Emulator 0.6
# Single File
# Mapper 0 NROM Base
# Python 3.14
# ==========================================

import tkinter as tk
from tkinter import filedialog
import time


WIDTH = 256
HEIGHT = 240
SCALE = 2
FPS = 60


# ==========================
# CARTRIDGE
# ==========================

class Cartridge:

    def __init__(self):
        self.prg = bytes()
        self.chr = bytes()


    def load(self, path):

        with open(path, "rb") as f:
            data = f.read()


        if data[0:4] != b"NES\x1a":
            raise Exception("Not an NES ROM")


        prg_banks = data[4]
        chr_banks = data[5]

        offset = 16

        self.prg = data[
            offset:
            offset + prg_banks * 16384
        ]

        offset += prg_banks * 16384


        self.chr = data[
            offset:
            offset + chr_banks * 8192
        ]


        print(
            "Loaded PRG:",
            len(self.prg),
            "CHR:",
            len(self.chr)
        )



# ==========================
# NES BUS
# ==========================

class Bus:

    def __init__(self):

        self.cart = None

        self.ram = [
            0
            for _ in range(2048)
        ]


    def connect(self, cart):
        self.cart = cart


    def read(self, addr):

        addr &= 0xFFFF


        # CPU RAM
        if addr < 0x2000:

            return self.ram[
                addr & 0x07FF
            ]


        # PRG ROM
        if addr >= 0x8000:

            index = addr - 0x8000

            if len(self.cart.prg) == 16384:
                index &= 0x3FFF

            return self.cart.prg[index]


        return 0



    def write(self, addr, value):

        addr &= 0xFFFF


        if addr < 0x2000:

            self.ram[
                addr & 0x07FF
            ] = value & 255



# ==========================
# 6502 CPU
# ==========================

class CPU6502:


    def __init__(self,bus):

        self.bus = bus

        self.a = 0
        self.x = 0
        self.y = 0

        self.sp = 0xFD
        self.status = 0x24

        self.pc = 0


    def read(self,a):
        return self.bus.read(a)


    def reset(self):

        lo = self.read(0xFFFC)
        hi = self.read(0xFFFD)

        self.pc = lo | (hi << 8)


    def step(self):

        opcode = self.read(self.pc)

        self.pc += 1


        # NOP
        if opcode == 0xEA:
            pass


        # LDA immediate
        elif opcode == 0xA9:

            value = self.read(self.pc)

            self.pc += 1

            self.a = value


        # TAX
        elif opcode == 0xAA:

            self.x = self.a


        # INX
        elif opcode == 0xE8:

            self.x = (self.x + 1) & 255


        else:

            print(
                "Unknown opcode:",
                hex(opcode),
                "PC:",
                hex(self.pc-1)
            )



# ==========================
# PPU DISPLAY
# ==========================

class PPU:


    def __init__(self):

        self.framebuffer = [
            [
                0
                for x in range(WIDTH)
            ]
            for y in range(HEIGHT)
        ]


    def draw(self):

        for y in range(HEIGHT):

            for x in range(WIDTH):

                self.framebuffer[y][x] = (
                    (x+y)
                    & 255
                )



# ==========================
# NES
# ==========================

class NES:


    def __init__(self):

        self.cart = Cartridge()

        self.bus = Bus()

        self.cpu = CPU6502(
            self.bus
        )

        self.ppu = PPU()


        self.running=False



    def load(self,path):

        self.cart.load(path)

        self.bus.connect(
            self.cart
        )

        self.cpu.reset()

        self.running=True



    def update(self):

        if not self.running:
            return


        for i in range(1000):
            self.cpu.step()


        self.ppu.draw()



# ==========================
# GUI
# ==========================

class GUI:


    def __init__(self):

        self.root=tk.Tk()

        self.root.title(
            "ByChatGPT NES Emulator 0.6"
        )


        self.nes=NES()


        self.canvas=tk.Canvas(
            self.root,
            width=WIDTH*SCALE,
            height=HEIGHT*SCALE
        )

        self.canvas.pack()


        tk.Button(
            self.root,
            text="LOAD ROM",
            command=self.load
        ).pack()


        self.loop()

        self.root.mainloop()



    def load(self):

        path=filedialog.askopenfilename(
            filetypes=[
                ("NES ROM","*.nes")
            ]
        )

        if path:
            self.nes.load(path)



    def draw(self):

        self.canvas.delete("all")

        for y in range(HEIGHT):

            for x in range(WIDTH):

                c=self.nes.ppu.framebuffer[y][x]

                color="#%02x%02x%02x"%(
                    0,
                    c,
                    255
                )

                self.canvas.create_rectangle(
                    x*SCALE,
                    y*SCALE,
                    x*SCALE+SCALE,
                    y*SCALE+SCALE,
                    fill=color,
                    outline=""
                )



    def loop(self):

        self.nes.update()

        self.draw()

        self.root.after(
            1000//FPS,
            self.loop
        )



if __name__=="__main__":
    GUI()
