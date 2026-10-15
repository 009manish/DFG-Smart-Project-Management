#include <stdio.h>

struct Process {
    int id;
    int burst;
    int priority;
    int waiting;
    int turnaround;
    int completed;
};

int main() {
    struct Process p[100];
    int n, i, done, time = 0, best;
    float totalWT = 0, totalTAT = 0;

    if (scanf("%d", &n) != 1 || n <= 0 || n > 100)
        return 1;

    for (i = 0; i < n; i++) {
        p[i].id = i + 1;
        p[i].completed = 0;

        if (scanf("%d %d", &p[i].burst,&p[i].priority) != 2)
            return 1;

        if (p[i].burst <= 0)
            return 1;
    }

    for (done = 0; done < n; done++) {
        best = -1;

        for (i = 0; i < n; i++) {
            if (!p[i].completed &&
                (best == -1 ||p[i].priority > p[best].priority)) {
                best = i;
            }
        }

        p[best].waiting = time;
        time += p[best].burst;
        p[best].turnaround = time;
        p[best].completed = 1;

        totalWT += p[best].waiting;
        totalTAT += p[best].turnaround;

        printf("Task %d | Priority: %d | WT: %d | TAT: %d\n", p[best].id, p[best].priority,p[best].waiting, p[best].turnaround);
    }

    printf("Average Waiting Time: %.2f\n", totalWT / n);
    printf("Average Turnaround Time: %.2f\n", totalTAT / n);

    return 0;
}