#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <sys/select.h>
#include <time.h>
// #include <math.h>

#include "viture.h"


static void imuCallback(uint8_t *data, uint16_t len, uint32_t ts)
{
    if (len >= 36)
    {   
        printf("start");
        fwrite(data + 20, 1, 4*4 , stdout);
        printf("\n");
        fflush(stdout);

        // float quaternionW = makeFloat(data + 20);
        // float quaternionX = makeFloat(data + 24);
        // float quaternionY = makeFloat(data + 28);
        // float quaternionZ = makeFloat(data + 32);
    }
}

static void mcuCallback(uint16_t msgid, uint8_t *data, uint16_t len, uint32_t ts)
{
// no op
}


void testing_loop() {
    // simulated output

    uint8_t data[16];
    
    srand(time(NULL)); 
    while (1) {
        for (int i = 0; i < 16; i++) { data[i] = rand()%255; }

        printf("start");
        fwrite(data, 1, 4*4 , stdout);
        printf("\n");
        fflush(stdout);

        sleep(1/60.);
    }
}


int main() {
    //testing_loop();  // uncomment for testing without a device handy

    bool init_result = init(imuCallback, mcuCallback);
    if (init_result == false) {
        exit(52); // failure for failed init cause        
    }
    set_imu(true);

    
    fd_set read_fds;
    struct timeval timeout;
    char input_buffer[256];

    while (1) {

        FD_ZERO(&read_fds);

        FD_SET(STDIN_FILENO, &read_fds);

        timeout.tv_sec = 0;
        timeout.tv_usec = 0;
        int result;

        int ready = select(STDIN_FILENO + 1, &read_fds, NULL, NULL, &timeout);

        if (ready == -1) {
            perror("select gave -1/unexected signal");
            exit(EXIT_FAILURE);
        } else if (ready > 0) {
            if (fgets(input_buffer, sizeof(input_buffer), stdin) != NULL) {
                    if (!strncmp("q", input_buffer, strlen("q"))) {
                        break;
                    }
            } else {
                perror("getting input failed");
                exit(EXIT_FAILURE);
            }
        }
    }

    set_imu(false);
    //deinit(); //for some reason it hangs here??
    return 0;
}

