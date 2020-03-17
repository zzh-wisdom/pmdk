// SPDX-License-Identifier: BSD-3-Clause
/* Copyright 2020, Intel Corporation */

/*
 * usc_none.c -- pmem2 usc function for non supported platform
 */

#include "libpmem2.h"

int
pmem2_source_device_id(const struct pmem2_source *src, char *id, size_t *len)
{
	return PMEM2_E_NOSUPP;
}

int
pmem2_source_device_usc(const struct pmem2_source *src, uint64_t *usc)
{
	return PMEM2_E_NOSUPP;
}
