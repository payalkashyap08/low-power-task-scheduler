import tkinter as tk
from tkinter import ttk  # Themed widgets
from tkinter import messagebox
import time
import threading # To run scheduling without freezing the GUI
import psutil   # For CPU info (install with: pip install psutil)

class Task:
    """Simple class to represent a task"""
    def __init__(self, task_id, priority, execution_time):
        self.id = task_id
        self.priority = priority
        self.execution_time = execution_time

    def __repr__(self):
        # How the task object represents itself (useful for debugging)
        return f"Task(id={self.id}, priority={self.priority}, time={self.execution_time})"

class TaskSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GUI Task Scheduler")
        # Make window slightly bigger
        self.root.geometry("650x550")

        self.tasks = []
        self.task_id_counter = 1
        self.scheduling_in_progress = False

        # --- Style ---
        self.style = ttk.Style()
        self.style.theme_use('clam') # Or 'alt', 'default', 'classic'

        # --- Frames for layout ---
        self.input_frame = ttk.Frame(root, padding="10")
        self.input_frame.grid(row=0, column=0, sticky="ew")

        self.list_frame = ttk.Frame(root, padding="10")
        self.list_frame.grid(row=1, column=0, sticky="nsew") # Expand list area

        self.control_frame = ttk.Frame(root, padding="10")
        self.control_frame.grid(row=2, column=0, sticky="ew")

        self.status_frame = ttk.Frame(root, padding="10")
        self.status_frame.grid(row=3, column=0, sticky="nsew") # Expand status area

        # Configure grid weights so list/status areas expand
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # --- Input Widgets ---
        ttk.Label(self.input_frame, text="Priority (1=High):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.priority_entry = ttk.Entry(self.input_frame, width=10)
        self.priority_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.input_frame, text="Exec Time (sec):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.time_entry = ttk.Entry(self.input_frame, width=10)
        self.time_entry.grid(row=0, column=3, padx=5, pady=5)

        self.add_button = ttk.Button(self.input_frame, text="Add Task", command=self.add_task)
        self.add_button.grid(row=0, column=4, padx=10, pady=5)

        # --- Task List Display (using Treeview) ---
        self.task_tree = ttk.Treeview(self.list_frame, columns=("ID", "Priority", "Time"), show="headings")
        self.task_tree.heading("ID", text="ID")
        self.task_tree.heading("Priority", text="Priority")
        self.task_tree.heading("Time", text="Est. Time (s)")

        self.task_tree.column("ID", width=50, anchor=tk.CENTER)
        self.task_tree.column("Priority", width=100, anchor=tk.CENTER)
        self.task_tree.column("Time", width=100, anchor=tk.CENTER)

        # Add scrollbar to Treeview
        tree_scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.task_tree.grid(row=0, column=0, sticky="nsew")
        tree_scrollbar.grid(row=0, column=1, sticky="ns")

        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        # --- Control Widgets ---
        self.start_button = ttk.Button(self.control_frame, text="Start Scheduling", command=self.start_scheduling)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.cores_label = ttk.Label(self.control_frame, text="CPU Cores: ?")
        self.cores_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.cpu_load_label = ttk.Label(self.control_frame, text="CPU Load: ?.?%")
        self.cpu_load_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        # --- Status Area ---
        self.status_text = tk.Text(self.status_frame, height=10, wrap=tk.WORD, state=tk.DISABLED, relief=tk.SUNKEN, borderwidth=1)

        # Add scrollbar to status Text
        status_scrollbar = ttk.Scrollbar(self.status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)

        self.status_text.grid(row=0, column=0, sticky="nsew")
        status_scrollbar.grid(row=0, column=1, sticky="ns")

        self.status_frame.grid_rowconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(0, weight=1)

        # --- Initial Setup ---
        self.update_status("Welcome! Add tasks and click 'Start Scheduling'.")
        self.update_cpu_info() # Start periodic CPU info update

    def log_status(self, message):
        """Appends a message to the status text box safely from any thread."""
        # Make sure GUI updates happen in the main thread
        def append_text():
            self.status_text.config(state=tk.NORMAL)
            self.status_text.insert(tk.END, message + "\n")
            self.status_text.see(tk.END) # Scroll to the end
            self.status_text.config(state=tk.DISABLED)
        self.root.after(0, append_text) # Schedule the update

    def update_status(self, message):
        """Clears and sets the status text box safely."""
        def set_text():
            self.status_text.config(state=tk.NORMAL)
            self.status_text.delete('1.0', tk.END)
            self.status_text.insert('1.0', message + "\n")
            self.status_text.see(tk.END)
            self.status_text.config(state=tk.DISABLED)
        self.root.after(0, set_text)

    def update_cpu_info(self):
        """Gets CPU info and updates labels. Schedules itself to run again."""
        try:
            cores = psutil.cpu_count(logical=True) # Get logical core count
            # Get CPU percent over a short interval to avoid blocking
            # Run this part in a thread to avoid slight GUI lag
            threading.Thread(target=self._get_cpu_percent_async, daemon=True).start()
            self.cores_label.config(text=f"CPU Cores: {cores}")
        except Exception as e:
            self.cores_label.config(text="CPU Cores: Error")
            self.cpu_load_label.config(text="CPU Load: Error")
            print(f"Error getting CPU info: {e}") # Log error to console

        # Schedule next update
        self.root.after(2000, self.update_cpu_info) # Update every 2 seconds

    def _get_cpu_percent_async(self):
        """Helper to get CPU percentage without blocking main thread"""
        try:
            # Interval > 0 is recommended for accuracy
            cpu_load = psutil.cpu_percent(interval=0.1)
            # Schedule the label update back on the main thread
            self.root.after(0, lambda: self.cpu_load_label.config(text=f"CPU Load: {cpu_load:.1f}%"))
        except Exception as e:
             self.root.after(0, lambda: self.cpu_load_label.config(text="CPU Load: Error"))
             print(f"Error getting CPU percent: {e}")


    def add_task(self):
        """Adds a task from the input fields to the list and Treeview."""
        if self.scheduling_in_progress:
             messagebox.showwarning("Busy", "Cannot add tasks while scheduling is in progress.")
             return

        try:
            priority_str = self.priority_entry.get()
            time_str = self.time_entry.get()

            if not priority_str or not time_str:
                messagebox.showerror("Input Error", "Please enter both Priority and Execution Time.")
                return

            priority = int(priority_str)
            execution_time = int(time_str)

            if priority <= 0 or execution_time <= 0:
                messagebox.showerror("Input Error", "Priority and Execution Time must be positive integers.")
                return

            # Create and add the task
            new_task = Task(self.task_id_counter, priority, execution_time)
            self.tasks.append(new_task)
            self.task_id_counter += 1

            # Add to Treeview
            self.task_tree.insert("", tk.END, values=(new_task.id, new_task.priority, new_task.execution_time))

            # Clear input fields
            self.priority_entry.delete(0, tk.END)
            self.time_entry.delete(0, tk.END)
            self.priority_entry.focus_set() # Set focus back to priority

            self.log_status(f"Added Task {new_task.id} (Prio: {new_task.priority}, Time: {new_task.execution_time}s)")

        except ValueError:
            messagebox.showerror("Input Error", "Priority and Execution Time must be valid integers.")
        except Exception as e:
             messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def start_scheduling(self):
        """Starts the task scheduling process in a separate thread."""
        if self.scheduling_in_progress:
            messagebox.showwarning("Busy", "Scheduling is already in progress.")
            return

        if not self.tasks:
            messagebox.showinfo("No Tasks", "Please add some tasks before scheduling.")
            return

        # Disable buttons
        self.add_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)
        self.scheduling_in_progress = True
        self.update_status("Starting scheduling process...")

        # Run the actual scheduling logic in a separate thread
        # Pass a copy of the task list to avoid modification issues
        schedule_thread = threading.Thread(target=self.run_schedule, args=(list(self.tasks),), daemon=True)
        schedule_thread.start()

    def run_schedule(self, tasks_to_run):
        """The core scheduling logic (runs in a separate thread)."""
        try:
            # Sort tasks by priority (lower number = higher priority)
            tasks_to_run.sort(key=lambda task: task.priority)

            self.log_status("\n=== Scheduling Tasks (Sorted by Priority) ===")
            self.log_status(f"Detected Cores: {psutil.cpu_count(logical=True)}") # Log core count

            for task in tasks_to_run:
                # --- Power Management Simulation ---
                try:
                    # Get current CPU load just before potentially running
                    # Use interval for better accuracy, but short to be responsive
                    current_cpu_load = psutil.cpu_percent(interval=0.1)
                    self.log_status(f"Current CPU Load: {current_cpu_load:.1f}%")

                    if current_cpu_load > 75.0:
                        self.log_status(f"!! High CPU ({current_cpu_load:.1f}%)! Delaying Task {task.id}...")
                        time.sleep(3) # Delay for 3 seconds
                        # Optionally re-check load here
                        current_cpu_load = psutil.cpu_percent(interval=0.1)
                        self.log_status(f"CPU Load after delay: {current_cpu_load:.1f}%")

                except Exception as e:
                     self.log_status(f"Warning: Could not get CPU load - {e}")


                # --- Execute Task (Simulated) ---
                self.log_status(f"--> Executing Task {task.id} | Prio: {task.priority} | Time: {task.execution_time}s")
                start_time = time.time()

                # Simulate work
                time.sleep(task.execution_time)

                end_time = time.time()
                duration = end_time - start_time
                self.log_status(f"<-- Task {task.id} completed in {duration:.2f} seconds.")

            self.log_status("\n=== All tasks executed. ===")
            self.log_status("Simulating entering low-power mode...")
            time.sleep(1) # Short pause at the end

        except Exception as e:
            # Log any unexpected error during scheduling
            self.log_status(f"\n!!! ERROR during scheduling: {e} !!!")
            messagebox.showerror("Scheduling Error", f"An error occurred during scheduling:\n{e}", parent=self.root) # Show error in GUI too
        finally:
            # --- Re-enable buttons (must be done in main thread) ---
            def enable_buttons():
                self.add_button.config(state=tk.NORMAL)
                self.start_button.config(state=tk.NORMAL)
                self.scheduling_in_progress = False
                self.log_status("Scheduler finished. Ready for more tasks.")
            self.root.after(0, enable_buttons)


# --- Main Execution ---
if __name__ == "__main__":
    main_window = tk.Tk()
    app = TaskSchedulerApp(main_window)
    main_window.mainloop()
