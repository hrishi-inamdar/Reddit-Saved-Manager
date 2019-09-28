from tkinter import *
from tkinter import messagebox
import helper
import requests
import webbrowser
from PIL import Image, ImageTk
from io import BytesIO

HEIGHT = 800
WIDTH = 900
OFFSETX = 0
OFFSETY = 0

COLUMNS = 6

saved_list = []
old_saved_list = []

# TODO: add up and down arrows to move posts up/down only one space
def populate_frame(frame):
    def _on_arrow_click(is_up, row):
        other = 0
        children = frame.winfo_children()
        if is_up:
            other = row - 1
            if other < 0:
                return
        else:
            other = row + 1
            if other > len(saved_list) - 1:
                return
        sub = saved_list[row]
        other_sub = saved_list[other]

        try:
            url = sub.thumbnail
        except:
            url = 'default'
        if url == 'self' or url == 'default' or url == 'spoiler':  # ie there is no thumbnail
            img1 = PhotoImage(file='./assets/placeholder150px.png')
        else:
            response = requests.get(url)
            pil_img = Image.open(BytesIO(response.content))
            img1 = ImageTk.PhotoImage(pil_img)
        try:
            url = other_sub.thumbnail
        except:
            url = 'default'
        if url == 'self' or url == 'default' or url == 'spoiler':  # ie there is no thumbnail
            img2 = PhotoImage(file='./assets/placeholder150px.png')
        else:
            response = requests.get(url)
            pil_img = Image.open(BytesIO(response.content))
            img2 = ImageTk.PhotoImage(pil_img)
        try:
            title = sub.title
        except:
            title = '<<<COMMENTS NOT SUPPORTED (yet)>>>'
        try:
            other_title = other_sub.title
        except:
            other_title = '<<<COMMENTS NOT SUPPORTED (yet)>>>'

        title = list(title)
        other_title = list(other_title)
        for m in range(len(title)):
            if ord(title[m]) > 65535:
                title[m] = '?'
        for n in range(len(other_title)):
            if ord(other_title[n]) > 65535:
                other_title[n] = '?'
        title = ''.join(title)
        other_title = ''.join(other_title)

        children[other * COLUMNS + 3].configure(image=img1)
        children[other * COLUMNS + 3].image = img1  # this is so that it won't get garbage collected
        children[other * COLUMNS + 4].configure(text=title)

        children[row * COLUMNS + 3].configure(image=img2)
        children[row * COLUMNS + 3].image = img2
        children[row * COLUMNS + 4].configure(text=other_title)

        # swap the entries in the saved_list
        temp = saved_list[row]
        saved_list[row] = saved_list[other]
        saved_list[other] = temp

    def _on_thumb_click(row):
        webbrowser.open_new(saved_list[row].url)

    def _on_unsave(row):
        result = messagebox.askyesno('Unsave', 'Are you sure you want to unsave this post?\nTitle: \"' + saved_list[row].title + '\"', icon='warning')
        if not result:
            return
        saved_list[row].unsave()
        sub = saved_list.pop(row)
        old_saved_list.remove(sub)
        update(frame.master)

    global saved_list
    for i in range(len(saved_list)):
        submission = saved_list[i]

        frame.rowconfigure('all', minsize=50)
        frame.columnconfigure(2, minsize=600)
        up_img = PhotoImage(file='./assets/up2.png')
        down_img = PhotoImage(file='./assets/down2.png')
        up = Label(frame, image=up_img, bg='white')
        down = Label(frame, image=down_img, bg='white')
        up.image = up_img
        down.image = down_img
        up.bind('<Button-1>', lambda event, is_up=True, row=i: _on_arrow_click(is_up, row))
        down.bind('<Button-1>', lambda event, is_up=False, row=i: _on_arrow_click(is_up, row))
        up.grid(row=3 * i)
        down.grid(row=3 * i + 2)

        rank_box = Text(frame, height=1, width=3, padx=5, pady=5)
        rank_box.insert(END, str(len(saved_list) - i))
        rank_box.grid(row=3 * i + 1, column=0, padx=5)

        try:
            url = submission.thumbnail
        except:
            url = 'default'
        if url == 'self' or url == 'default' or url == 'spoiler':  # ie there is no thumbnail
            img = PhotoImage(file='./assets/placeholder150px.png')
        else:
            response = requests.get(url)
            pil_img = Image.open(BytesIO(response.content))
            img = ImageTk.PhotoImage(pil_img)
        thumb = Label(frame, image=img, relief=GROOVE)
        thumb.image = img
        thumb.grid(row=3 * i, column=1, rowspan=3, padx=5)
        thumb.bind('<Button-1>', lambda event, row=i: _on_thumb_click(row))

        try:
            title = submission.title
        except:
            title = '<<<COMMENTS NOT SUPPORTED (yet)>>>'
        title = list(title)

        for j in range(len(title)):
            if ord(title[j]) > 65535:
                title[j] = '?'
        title = ''.join(title)
        title = Label(frame, text=title, wraplength=500, bg='white', font=("Helvetica", 16))
        title.grid(row=3 * i, column=2, rowspan=3, sticky='w')

        unsave = Button(frame, command=lambda row=i: _on_unsave(row), text='unsave')
        unsave.grid(row=3 * i + 1, column=3)


def get_ranks(frame):
    '''
        :param frame: contains list of posts in gui form
        :return: list of ranks as integers
    '''
    child_list = frame.winfo_children()  # grabs the grid of stuff
    rank_boxes = child_list[2::COLUMNS]  # grabs only the text box widgets
    ranks = []
    for box in rank_boxes:
        num = box.get('0.0', END)[0:-1]
        if num == '':
            num = '0'
        ranks += [int(num)]
    return ranks


def update(canvas):
    global saved_list
    global old_saved_list
    child = canvas.winfo_children()
    if not child:  # ie if this is the first time creating the frame...
        saved_list = helper.get_list()  # grab the saved list from praw
        old_saved_list = helper.get_list()
    else:
        frame = child[0]
        ranks = get_ranks(frame)
        _, saved_list = zip(*sorted(zip(ranks, saved_list), key=lambda x: x[0], reverse=True))
        saved_list = list(saved_list)
        frame.destroy()
    frame = Frame(canvas, bg='white')
    canvas.create_window((0, 0), window=frame, anchor='nw')

    canvas.bind("<Configure>", lambda event, can=canvas, fr=frame: _on_config(can, frame))
    canvas.bind_all("<MouseWheel>", lambda event, can=canvas: _on_mousewheel(event, can))
    canvas.bind_all("<Up>", lambda event, can=canvas, is_up=True: _on_arrowkey(can, is_up))
    canvas.bind_all("<Down>", lambda event, can=canvas, is_up=False: _on_arrowkey(can, is_up))
    populate_frame(frame)


def export():
    result = messagebox.askyesno('Export', 'Are you sure you want to export? This may take a while', icon='warning')
    if result:
        helper.export_to_reddit(old_saved_list, saved_list)
        messagebox.showinfo('Success', 'Your changes have been saved!')
    else:
        messagebox.showinfo('Canceled', 'Your changes have not been exported yet')


def setup_gui():
    root = Tk()
    root.title('Reddit Saved Manager')
    root.wm_geometry("%dx%d+%d+%d" % (WIDTH, HEIGHT, OFFSETX, OFFSETY))
    myframe = Frame(root, relief=GROOVE, width=100, height=100, bd=1)
    myframe.pack(fill='x')
    # myframe.grid(row=0, column=0, columnspan=3, rowspan=10)
    canvas = Canvas(myframe)
    update(canvas)
    update_button = Button(root, command=lambda can=canvas: update(can), text='update')
    export_button = Button(root, command=export, text='export')
    myscrollbar = Scrollbar(myframe, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=myscrollbar.set, bg='white')

    myscrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", expand=1, fill='x')
    update_button.pack(side='bottom', fill='x')
    export_button.pack(side='bottom', fill='x')

    return root


def _on_config(canvas, frame):
    canvas.configure(scrollregion=frame.bbox("all"), width=WIDTH - 40, height=HEIGHT - 100)


def _on_mousewheel(event, canvas):
    raw = event.delta
    # mag = abs(raw) ** (1 / 2)
    if raw != 0:
        dir = raw / (abs(raw))
        canvas.yview_scroll(-1 * int(dir), "units")


def _on_arrowkey(canvas, is_up):
    val = -1 if is_up else 1
    canvas.yview_scroll(val, "units")


def main():
    root = setup_gui()
    root.mainloop()


if __name__ == '__main__':
    main()
