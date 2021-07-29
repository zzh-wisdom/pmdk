#!../env.py
# SPDX-License-Identifier: BSD-3-Clause
# Copyright 2020-2021, Intel Corporation
#

import testframework as t
from testframework import granularity as g
import os


@g.require_granularity(g.ANY)
class PMEMSET_SOURCE(t.Test):
    test_type = t.Short
    create_file = True

    def run(self, ctx):
        if self.create_file:
            filepath = ctx.create_holey_file(16 * t.MiB, 'testfile1')
        else:
            filepath = os.path.join(ctx.testdir, 'testfile1')

        ctx.exec('pmemset_source', self.test_case, filepath)
        if os.path.exists(filepath):
            os.remove(filepath)


@g.no_testdir()
class PMEMSET_SOURCE_NO_DIR(t.Test):
    test_type = t.Short

    def run(self, ctx):
        ctx.exec('pmemset_source', self.test_case)


class PMEMSET_SOURCE_DIR_ONLY(t.Test):
    test_type = t.Short
    do_not_close = False

    def run(self, ctx):
        if self.do_not_close:
            ctx.env['UNITTEST_DO_NOT_FAIL_OPEN_FILES'] = '1'
        ctx.exec('pmemset_source', self.test_case, ctx.testdir)


class TEST0(PMEMSET_SOURCE):
    """allocation of pmemset_source in case of missing memory in system"""
    test_case = "test_alloc_src_enomem"


class TEST1(PMEMSET_SOURCE_NO_DIR):
    """testing pmemset_from_pmem2 with null value"""
    test_case = "test_set_from_pmem2_null"


class TEST2(PMEMSET_SOURCE):
    """valid allocation of pmemset_source from pmem2"""
    test_case = "test_set_from_pmem2_valid"


class TEST3(PMEMSET_SOURCE_NO_DIR):
    """test source creation from null file path"""
    test_case = "test_src_from_file_null"


class TEST4(PMEMSET_SOURCE):
    """test source creation with valid file path"""
    test_case = "test_src_from_file_valid"


class TEST5(PMEMSET_SOURCE):
    """test source creation with existing file and create_always flag set"""
    test_case = "test_src_from_file_exists_always_disp"


class TEST6(PMEMSET_SOURCE):
    """test source creation with no existing file and create_always flag set"""
    test_case = "test_src_from_file_not_exists_always_disp"
    create_file = False


class TEST7(PMEMSET_SOURCE):
    """test source creation with existing file and if_needed flag set"""
    test_case = "test_src_from_file_exists_needed_disp"


class TEST8(PMEMSET_SOURCE):
    """test source creation with no existing file and if_needed flag set"""
    test_case = "test_src_from_file_not_exists_needed_disp"
    create_file = False


class TEST9(PMEMSET_SOURCE):
    """test source creation with invalid flags"""
    test_case = "test_src_from_file_invalid_flags"


class TEST10(PMEMSET_SOURCE_DIR_ONLY):
    """testing pmemset_from_temporary valid case"""
    test_case = "test_src_from_temporary_valid"


class TEST11(PMEMSET_SOURCE_NO_DIR):
    """testing pmemset_from_temporary invalid dir"""
    test_case = "test_src_from_temporary_inval_dir"


class TEST12(PMEMSET_SOURCE_DIR_ONLY):
    """testing pmemset_from_temporary and skip pmemset source delete"""
    test_case = "test_src_from_temporary_no_del"
    do_not_close = True


class TEST13(PMEMSET_SOURCE):
    """test source creation with no existing file and truncate flag set"""
    test_case = "test_src_from_file_with_truncate"
    create_file = False
