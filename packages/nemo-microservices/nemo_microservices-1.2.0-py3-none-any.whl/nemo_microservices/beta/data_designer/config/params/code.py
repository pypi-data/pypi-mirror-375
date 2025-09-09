# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from enum import Enum


class CodeLang(str, Enum):
    GO = "go"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    KOTLIN = "kotlin"
    PYTHON = "python"
    RUBY = "ruby"
    RUST = "rust"
    SCALA = "scala"
    SWIFT = "swift"
    TYPESCRIPT = "typescript"
    SQL_SQLITE = "sql:sqlite"
    SQL_TSQL = "sql:tsql"
    SQL_BIGQUERY = "sql:bigquery"
    SQL_MYSQL = "sql:mysql"
    SQL_POSTGRES = "sql:postgres"
    SQL_ANSI = "sql:ansi"


SQL_DIALECTS: set[CodeLang] = {
    CodeLang.SQL_SQLITE,
    CodeLang.SQL_TSQL,
    CodeLang.SQL_BIGQUERY,
    CodeLang.SQL_MYSQL,
    CodeLang.SQL_POSTGRES,
    CodeLang.SQL_ANSI,
}

##########################################################
# Helper functions
##########################################################


def code_lang_to_syntax_lexer(code_lang: CodeLang | str) -> str:
    """Convert the code language to a syntax lexer for Pygments.

    Reference: https://pygments.org/docs/lexers/
    """
    code_lang_to_lexer = {
        CodeLang.GO: "golang",
        CodeLang.JAVASCRIPT: "javascript",
        CodeLang.JAVA: "java",
        CodeLang.KOTLIN: "kotlin",
        CodeLang.PYTHON: "python",
        CodeLang.RUBY: "ruby",
        CodeLang.RUST: "rust",
        CodeLang.SCALA: "scala",
        CodeLang.SWIFT: "swift",
        CodeLang.SQL_SQLITE: "sql",
        CodeLang.SQL_ANSI: "sql",
        CodeLang.SQL_TSQL: "tsql",
        CodeLang.SQL_BIGQUERY: "sql",
        CodeLang.SQL_MYSQL: "mysql",
        CodeLang.SQL_POSTGRES: "postgres",
    }
    return code_lang_to_lexer.get(code_lang, code_lang)
