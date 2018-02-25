#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <arpa/inet.h>

void main() {
	int client_sock;
	int listen_sock;
	struct sockaddr_in client_addr;
	struct sockaddr_in listen_addr;
	int status = 0;

	listen_sock = socket(AF_INET, SOCK_STREAM, 0);
	if (listen_sock < 0) {
		printf("Socket Error\n");
		return;
	}

	listen_addr.sin_family = AF_INET;
	listen_addr.sin_port = htons(7000);
	listen_addr.sin_addr.s_addr = htonl(INADDR_ANY);
	status = bind(listen_sock, (struct sockaddr*)&listen_addr, sizeof(listen_addr));
	if (status == -1) {
		printf("Bing Error\n");
		return;
	}

	status = listen(listen_sock, 5);
	if (status == -1) {
		printf("Listen Error\n");
		return;
	}

	unsigned int client_addr_size = sizeof(client_addr)

	{
		client_sock = accept(listen_sock, (struct sockaddr*)&client_addr, &client_addr_size);
		if (client_sock < 0) {
			printf("Accept Error\n");
			return;
		}

		printf("Connection from %s:%d on socket %d\n", 
				inet_ntoa(client_addr.sin_addr),
				ntohs(client_addr.sin_port),
				client_sock);

		char buf[100];
		int len = 0;
		len = recv(client_sock, buf, 99, 0);
		buf[len] = '\0';

		shutdown(client_sock, SHUT_RDWR);
		close(client_sock);
	}

	shutdown(listen_sock, SHUT_RDWR);
	close(listen_sock);
}