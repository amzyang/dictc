#include <stdlib.h>

	int *
parse_idx(const char *data, int filesize, int count, int size)
{
	int pos = 0;
	int *container = (int *) malloc(sizeof(int) * count);
	int *ptr = container;
	while (pos < filesize) {
		while (data[pos] != '\0')
			pos++;
		pos += size + 1;
		*ptr = pos;
		ptr++;
	}
	return container;
}
