#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>  
#include <time.h>

#ifdef _WIN32
    #include <windows.h>  
#else
    #include <sys/sysinfo.h>  
    #include <sys/resource.h> 
    #include <sys/sysinfo.h>
#endif

#define MAX_TASKS 10

typedef struct {
    int id;
    int priority;
    int execution_time;
} Task;

// Function to get system CPU load
float getCPUUsage() {
#ifdef _WIN32
    FILETIME idleTime, kernelTime, userTime;
    if (GetSystemTimes(&idleTime, &kernelTime, &userTime)) {
        return (float)(userTime.dwLowDateTime + kernelTime.dwLowDateTime) / 100000.0;
    }
    return -1;  
#else
    struct sysinfo info;
    if (sysinfo(&info) == 0) {
        return 100.0 - ((info.loads[0] * 100.0) / (1 << SI_LOAD_SHIFT));
    }
    return -1;
#endif
}

// Function to get number of CPU cores
int getCPUCores() {
#ifdef _WIN32
    SYSTEM_INFO sysInfo;
    GetSystemInfo(&sysInfo);
    return sysInfo.dwNumberOfProcessors;
#else
    return sysconf(_SC_NPROCESSORS_ONLN);
#endif
}

//Sorting task (based on priority)
void sortTasks(Task tasks[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = i + 1; j < n; j++) {
            if (tasks[i].priority > tasks[j].priority) {
                Task temp = tasks[i];
                tasks[i] = tasks[j];
                tasks[j] = temp;
            }
        }
    }
}

// Function to execute tasks efficiently with dynamic power management
void scheduleTasks(Task tasks[], int n) {
    if (n == 0) {
        printf("No tasks available. CPU is entering low-power mode...\n");
        sleep(2);
        return;
    }

    printf("\n=== Scheduling tasks based on priority ===\n");
    int cpuCores = getCPUCores();
    printf("Detected CPU Cores: %d\n", cpuCores);

    for (int i = 0; i < n; i++) {
        float cpuLoad = getCPUUsage();
        printf("Current CPU Load: %.2f%%\n", cpuLoad);

        if (cpuLoad > 75.0) {
            printf("?? High CPU usage detected! Delaying execution to save power...\n");
            sleep(3);
        }
        
        time_t startTime = time(NULL);
        printf("Executing Task %d | Priority: %d | Execution Time: %d sec\n",
               tasks[i].id, tasks[i].priority, tasks[i].execution_time);
        sleep(tasks[i].execution_time);

        time_t endTime = time(NULL);
        printf("? Task %d completed in %ld seconds\n", tasks[i].id, (endTime - startTime));
    }

    printf("\nAll tasks executed. CPU entering low-power mode...\n");
    sleep(2);
}

int main() {
    int n;
    Task tasks[MAX_TASKS];

    // Get the number of tasks
    printf("Enter number of tasks (Max %d): ", MAX_TASKS);
    if (scanf("%d", &n) != 1 || n <= 0 || n > MAX_TASKS) {
        printf("Invalid input! Please enter a number between 1 and %d.\n", MAX_TASKS);
        return 1;
    }

    while (getchar() != '\n'); // Clear input buffer

    for (int i = 0; i < n; i++) {
        printf("\nEnter details for Task %d:\n", i + 1);
        tasks[i].id = i + 1;

        printf("Priority (Lower value = Higher priority): ");
        if (scanf("%d", &tasks[i].priority) != 1) {
            printf("Invalid input! Exiting...\n");
            return 1;
        }

        printf("Execution Time (in seconds): ");
        if (scanf("%d", &tasks[i].execution_time) != 1) {
            printf("Invalid input! Exiting...\n");
            return 1;
        }

        while (getchar() != '\n'); // Clear buffer
    }

    // Sort tasks by priority
    sortTasks(tasks, n);

    // Schedule tasks efficiently
    scheduleTasks(tasks, n);

    return 0;
}