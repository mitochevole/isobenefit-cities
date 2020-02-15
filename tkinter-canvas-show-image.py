# import glob
# # import json
# # import os
# # from tkinter import *
# # from PIL import Image, ImageTk
# #
# #
# # def get_most_recent_snapshot_filepath(metadata='temp_metadata'):
# #     with open(metadata, 'r') as f:
# #         output_path = json.loads(f.read())['output_path']
# #     list_of_files = glob.glob(output_path + '/*.png')  # * means all if need specific format then *.csv
# #     latest_file = max(list_of_files, key=os.path.getctime)
# #     return latest_file
# #
# #
# # def update_gui_canvas(gui_canvas):
# #     final_path = get_most_recent_snapshot_filepath()
# #     print(final_path)
# #     pilImage = Image.open(final_path)
# #     image = ImageTk.PhotoImage(pilImage)
# #     gui_canvas.create_image(100, 100, image=image)
# #     gui_canvas.after(500,update_gui_canvas(gui_canvas))
# #
# #
# #
# # if __name__ == '__main__':
# #
# #     root = Tk()
# #     root.title("isobenefit-cities")
# #     root.resizable(False,False)
# #     canvas = Canvas(root, width = 300, height = 300)
# #     canvas.pack()
# #     final_path = get_most_recent_snapshot_filepath('temp_metadata')
# #     update_gui_canvas(canvas)
# #
# #
# #     root.mainloop()

#
# from tkinter import *
# from random import randint
# import numpy as np
#
# class Ball:
#     def __init__(self, canvas, x1, y1, x2, y2):
#         self.x1 = x1
#         self.y1 = y1
#         self.x2 = x2
#         self.y2 = y2
#         self.canvas = canvas
#         self.ball = canvas.create_oval(self.x1, self.y1, self.x2, self.y2, fill="red")
#
#     def move_ball(self):
#         deltax = np.random.randn()*5
#         deltay = np.random.randn()*5
#         self.canvas.move(self.ball, deltax, deltay)
#         self.canvas.after(50, self.move_ball)
#
# if __name__ == '__main__':
# # initialize root Window and canvas
#     root = Tk()
#     root.title("Balls")
#     root.resizable(False,False)
#     canvas = Canvas(root, width = 1000, height = 500)
#     canvas.pack()
#
#     # create a swarm of ball objects and animate them
#     swarm_of_balls = [ Ball(canvas, 500, 250, 520, 270) for _ in range(100)]
#
#     [s.move_ball() for s in swarm_of_balls]
#
#     root.mainloop()