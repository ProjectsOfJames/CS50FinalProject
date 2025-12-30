import tkinter as tk

def main():
    root = tk.Tk()
    root.title("RecorderX")
    root.geometry("400x300")

    label = tk.Label(root, text="RecorderX is running")
    label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
