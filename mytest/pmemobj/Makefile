CC = gcc
CFLAGS = #-std=c++11 #-ggdb -Wall -Werror
LDFLAGS = -lpmemobj -lpmem

RM = rm -f

obj_write_test = bin/obj_write_test
obj_read_test = bin/obj_read_test
TARGETS = $(obj_write_test) $(obj_read_test)

.PHONY: all clean test clean-data-files

all: $(TARGETS)

$(obj_write_test):
	$(CC) $(CFLAGS) -o $@ obj_write_test.c $(LDFLAGS)

$(obj_read_test):
	$(CC) $(CFLAGS) -o $@ obj_read_test.c $(LDFLAGS)

test: clean-data-files
	@echo "请输入您的对象(< 10 bytes):"
	@./bin/obj_write_test ./pmem-fs/obj-fs
	@echo "读取对象的结果为:"
	@./bin/obj_read_test ./pmem-fs/obj-fs

clean-data-files:
	$(RM) ./pmem-fs/*

clean:
	$(RM) ./bin/* ./pmem-fs/*