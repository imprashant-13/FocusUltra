Created by Prashant

---------------------------------------------------------------------------------------------------------------------------


Focus Ultra

Focus Ultra is a small desktop focus app I made mainly for fun and personal use.

It’s meant to be simple, calm, and easy to use — nothing serious, nothing overengineered.

-------------------------------------------------------------------------------------------------------------------------------------------------


What it does:


⇉Dashboard

1.Add daily goals

2.Simple input and quick actions

3.Minimal layout to avoid distractions




⇉Analytics

1.Shows how much you completed today

2.Tracks active days

3.Keeps count of perfect days (when you finish everything)

4.Basic last 7 days activity view




⇉Settings

1.Toggle sound effects

2.Clear all local data if you want a fresh start



⇉Design

1.Dark theme

2.Clean layout

3.No notifications

4.No unnecessary features

The idea was to keep it comfortable to look at and easy to use for long sessions.




⇉Data and privacy

1.Everything is stored locally

2.No account required

3.No internet connection needed

4.Nothing is uploaded anywhere




⇉About the project:

This was a fun side project Built to experiment with UI and app flow.

It’s simple on purpose.


---------------------------------------------------------------------------------------------------------------------------



⇉Instructions:

1.Use 12 hrs format of time in your pc

2.If you dont want an executable file then directly use the following code in an integrated terminal

Bash
```
python main.py
```


---------------------------------------------------------------------------------------------------------------------------



⇉For creating .exe file(or an app) in your pc:

1.Install PyInstaller

Bash
```
pip install pyinstaller
```



2.Build the executable
Run this in the project folder(open an integrated terminal in the project folder):

Bash
```
pyinstaller --noconsole --onefile --icon=app.ico --name "FocusUltra" main.py
```


⇉What this does:

Creates a single .exe file

Hides the terminal window

Sets a custom app icon

Names the app FocusUltra


⇉Output

After the build completes, you’ll find the file here:
```
dist/FocusUltra.exe
```

The executable will show your custom icon in File Explorer and on the desktop shortcut.

---------------------------------------------------------------------------------------------------------------------------


⇉Note

1.First build may take some time

2.Windows Defender may show a warning (normal for unsigned executables)


