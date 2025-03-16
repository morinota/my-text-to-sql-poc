E2B Data Analysis | 🦜️🔗 LangChain  
E2Bデータ分析 | 🦜️🔗 LangChain  

E2B's cloud environments are great runtime sandboxes for LLMs.  
E2Bのクラウド環境は、LLMのための優れたランタイムサンドボックスです。  

E2B's Data Analysis sandbox allows for safe code execution in a sandboxed environment.  
E2Bのデータ分析サンドボックスは、サンドボックス環境での安全なコード実行を可能にします。  

This is ideal for building tools such as code interpreters, or Advanced Data Analysis like in ChatGPT.  
これは、コードインタープリタやChatGPTのような高度なデータ分析ツールを構築するのに最適です。  

E2B Data Analysis sandbox allows you to:  
E2Bデータ分析サンドボックスでは、次のことができます：  

- Run Python code  
Pythonコードを実行する  

- Generate charts via matplotlib  
matplotlibを使用してチャートを生成する  

- Install Python packages dynamically during runtime  
ランタイム中にPythonパッケージを動的にインストールする  

^ Install system packages dynamically during runtime  
ランタイム中にシステムパッケージを動的にインストールする  

- Run shell commands  
シェルコマンドを実行する  

- Upload and download files  
ファイルをアップロードおよびダウンロードする  

We'll create a simple OpenAI agent that will use E2B's Data Analysis sandbox to perform analysis on a uploaded files using Python.  
私たちは、**E2Bのデータ分析サンドボックスを使用して、アップロードされたファイルに対して分析を行うシンプルなOpenAIエージェント**を作成します。  

Get your OpenAI API key and E2B API key here and set them as environment variables.  
ここでOpenAI APIキーとE2B APIキーを取得し、それらを環境変数として設定します。  

You can find the full API documentation here.  
完全なAPIドキュメントはここにあります。  

You'll need to install e2b to get started:  
始めるには、e2bをインストールする必要があります：  

```  
%pip install --upgrade --quiet  langchain e2b langchain-community  
```  

```  
from langchain_community.tools import E2BDataAnalysisTool  
```  

API Reference:E2BDataAnalysisTool  
APIリファレンス：E2BDataAnalysisTool  

```  
import os

from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI

os.environ["E2B_API_KEY"] = "<E2B_API_KEY>"
os.environ["OPENAI_API_KEY"] = "<OPENAI_API_KEY>"
```

API Reference:AgentType | initialize_agent | ChatOpenAI  
APIリファレンス：AgentType | initialize_agent | ChatOpenAI  

When creating an instance of the E2BDataAnalysisTool, you can pass callbacks to listen to the output of the sandbox.  
E2BDataAnalysisToolのインスタンスを作成する際に、サンドボックスの出力をリッスンするためのコールバックを渡すことができます。  

This is useful, for example, when creating more responsive UI.  
これは、たとえば、より応答性の高いUIを作成する際に便利です。  

Especially with the combination of streaming output from LLMs.  
特に、LLMからのストリーミング出力と組み合わせると効果的です。  

# Artifacts are charts created by matplotlib when `plt.show()` is called

# アーティファクトは、`plt.show()`が呼び出されたときにmatplotlibによって作成されるチャートです

def save_artifact(artifact):
    print("New matplotlib chart generated:", artifact.name)
    # Download the artifact as `bytes` and leave it up to the user to display them (on frontend, for example)
    # アーティファクトを`bytes`としてダウンロードし、表示はユーザーに任せます（例えばフロントエンドで）。
    file = artifact.download()
    basename = os.path.basename(artifact.name)
    # Save the chart to the `charts` directory
    # チャートを`charts`ディレクトリに保存します。
    with open(f"./charts/{basename}", "wb") as f:
        f.write(file)

e2b_data_analysis_tool = E2BDataAnalysisTool(
    # Pass environment variables to the sandbox
    # 環境変数をサンドボックスに渡します。
    env_vars={"MY_SECRET": "secret_value"},
    on_stdout=lambda stdout: print("stdout:", stdout),
    on_stderr=lambda stderr: print("stderr:", stderr),
    on_artifact=save_artifact,
)

# Upload an example CSV data file to the sandbox so we can analyze it with our agent

# エージェントで分析できるように、サンドボックスに例のCSVデータファイルをアップロードします

You can use for example this file about Netflix tv shows.

# 例えば、Netflixのテレビ番組に関するこのファイルを使用できます

with open("./netflix.csv") as f:
    remote_path = e2b_data_analysis_tool.upload_file(
        file=f,
        description="Data about Netflix tv shows including their title, category, director, release date, casting, age rating, etc.",
    )
    print(remote_path)

name='netflix.csv' remote_path='/home/user/netflix.csv' description='Data about Netflix tv shows including their title, category, director, release date, casting, age rating, etc.'

# name='netflix.csv' remote_path='/home/user/netflix.csv' description='Netflixのテレビ番組に関するデータ（タイトル、カテゴリ、監督、リリース日、キャスト、年齢評価などを含む）'

# Create a Tool object and initialize the Langchain agent

# ツールオブジェクトを作成し、Langchainエージェントを初期化します

tools = [e2b_data_analysis_tool.as_tool()]
llm = ChatOpenAI(model="gpt-4", temperature=0)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    handle_parsing_errors=True,
)

# Now we can ask the agent questions about the CSV file we uploaded earlier

# これで、以前アップロードしたCSVファイルについてエージェントに質問できます

agent.run(
    "What are the 5 longest movies on netflix released between 2000 and 2010? Create a chart with their lengths."
)

# "2000年から2010年の間にリリースされたNetflixの最も長い映画5本は何ですか？それらの長さを示すチャートを作成してください。"

[1m> Entering new AgentExecutor chain...[0m

# [1m> 新しいAgentExecutorチェーンに入ります...[0m

[32;1m[1;3mInvoking: `e2b_data_analysis` with `{'python_code': "import pandas as pd\n\n# Load the data\nnetflix_data = pd.read_csv('/home/user/netflix.csv')\n\n# Convert the 'release_year' column to integer\nnetflix_data['release_year'] = netflix_data['release_year'].astype(int)\n\n# Filter the data for movies released between 2000 and 2010\nfiltered_data = netflix_data[(netflix_data['release_year'] >= 2000) & (netflix_data['release_year'] <= 2010) & (netflix_data['type'] == 'Movie')]\n\n# Remove rows where 'duration' is not available\nfiltered_data = filtered_data[filtered_data['duration'].notna()]\n\n# Convert the 'duration' column to integer\nfiltered_data['duration'] = filtered_data['duration'].str.replace(' min','').astype(int)\n\n# Get the top 5 longest movies\nlongest_movies = filtered_data.nlargest(5, 'duration')\n\n# Create a bar chart\nimport matplotlib.pyplot as plt\n\nplt.figure(figsize=(10,5))\nplt.barh(longest_movies['title'], longest_movies['duration'], color='skyblue')\nplt.xlabel('Duration (minutes)')\nplt.title('Top 5 Longest Movies on Netflix (2000-2010)')\nplt.gca().invert_yaxis()\nplt.savefig('/home/user/longest_movies.png')\n\nlongest_movies[['title', 'duration']]}"}`

# [32;1m[1;3m呼び出し中: `e2b_data_analysis` with `{'python_code': "import pandas as pd\n\n# データを読み込む\nnetflix_data = pd.read_csv('/home/user/netflix.csv')\n\n# 'release_year'列を整数に変換\nnetflix_data['release_year'] = netflix_data['release_year'].astype(int)\n\n# 2000年から2010年の間にリリースされた映画のデータをフィルタリング\nfiltered_data = netflix_data[(netflix_data['release_year'] >= 2000) & (netflix_data['release_year'] <= 2010) & (netflix_data['type'] == 'Movie')]\n\n# 'duration'が利用できない行を削除\nfiltered_data = filtered_data[filtered_data['duration'].notna()]\n\n# 'duration'列を整数に変換\nfiltered_data['duration'] = filtered_data['duration'].str.replace(' min','').astype(int)\n\n# 最も長い5本の映画を取得\nlongest_movies = filtered_data.nlargest(5, 'duration')\n\n# 棒グラフを作成\nimport matplotlib.pyplot as plt\n\nplt.figure(figsize=(10,5))\nplt.barh(longest_movies['title'], longest_movies['duration'], color='skyblue')\nplt.xlabel('Duration (minutes)')\nplt.title('Top 5 Longest Movies on Netflix (2000-2010)')\nplt.gca().invert_yaxis()\nplt.savefig('/home/user/longest_movies.png')\n\nlongest_movies[['title', 'duration']]}"}`

[0mstdout:                              title  duration

# [0mstdout:                              title  duration

1019                        Lagaan       224

# 1019                        Lagaan       224

4573                  Jodhaa Akbar       214

# 4573                  Jodhaa Akbar       214

2731      Kabhi Khushi Kabhie Gham       209

# 2731      Kabhi Khushi Kabhie Gham       209

2632  No Direction Home: Bob Dylan       208

# 2632  No Direction Home: Bob Dylan       208

2126          What's Your Raashee?       203

# 2126          What's Your Raashee?       203

[36;1m[1;3m{'stdout': "                             title  duration\n1019                        Lagaan       224\n4573                  Jodhaa Akbar       214\n2731      Kabhi Khushi Kabhie Gham       209\n2632  No Direction Home: Bob Dylan       208\n2126          What's Your Raashee?       203", 'stderr': ''}[0m

# [36;1m[1;3m{'stdout': "                             title  duration\n1019                        Lagaan       224\n4573                  Jodhaa Akbar       214\n2731      Kabhi Khushi Kabhie Gham       209\n2632  No Direction Home: Bob Dylan       208\n2126          What's Your Raashee?       203", 'stderr': ''}[0m

[32;1m[1;3mThe 5 longest movies on Netflix released between 2000 and 2010 are:

# [32;1m[1;3m2000年から2010年の間にリリースされたNetflixの最も長い映画5本は

1. Lagaan - 224 minutes

# 1. Lagaan - 224分

2. Jodhaa Akbar - 214 minutes

# 2. Jodhaa Akbar - 214分

3. Kabhi Khushi Kabhie Gham - 209 minutes

# 3. Kabhi Khushi Kabhie Gham - 209分

4. No Direction Home: Bob Dylan - 208 minutes

# 4. No Direction Home: Bob Dylan - 208分

5. What's Your Raashee? - 203 minutes

# 5. What's Your Raashee? - 203分

Here is the chart showing their lengths:

# こちらがそれらの長さを示すチャートです

![Longest Movies](sandbox:/home/user/longest_movies.png)

# ![Longest Movies](sandbox:/home/user/longest_movies.png)

[0m[1m> Finished chain.[0m

# [0m[1m> チェーンが終了しました。[0m

E2B also allows you to install both Python and system (via apt) packages dynamically during runtime like this:

# E2Bは、実行時にこのようにPythonおよびシステム（apt経由）のパッケージを動的にインストールすることも可能です

```

```md
# Install Python packagee2b_data_analysis_tool.install_python_packages("pandas")
# Pythonパッケージのインストールe2b_data_analysis_tool.install_python_packages("pandas")

stdout: Requirement already satisfied: pandas in /usr/local/lib/python3.10/dist-packages (2.1.1)
stdout: 要件はすでに満たされています: pandasは/usr/local/lib/python3.10/dist-packagesにあります (2.1.1)

stdout: Requirement already satisfied: python-dateutil>=2.8.2 in /usr/local/lib/python3.10/dist-packages (from pandas) (2.8.2)
stdout: 要件はすでに満たされています: python-dateutil>=2.8.2は/usr/local/lib/python3.10/dist-packagesにあります (pandasから) (2.8.2)

stdout: Requirement already satisfied: pytz>=2020.1 in /usr/local/lib/python3.10/dist-packages (from pandas) (2023.3.post1)
stdout: 要件はすでに満たされています: pytz>=2020.1は/usr/local/lib/python3.10/dist-packagesにあります (pandasから) (2023.3.post1)

stdout: Requirement already satisfied: numpy>=1.22.4 in /usr/local/lib/python3.10/dist-packages (from pandas) (1.26.1)
stdout: 要件はすでに満たされています: numpy>=1.22.4は/usr/local/lib/python3.10/dist-packagesにあります (pandasから) (1.26.1)

stdout: Requirement already satisfied: tzdata>=2022.1 in /usr/local/lib/python3.10/dist-packages (from pandas) (2023.3)
stdout: 要件はすでに満たされています: tzdata>=2022.1は/usr/local/lib/python3.10/dist-packagesにあります (pandasから) (2023.3)

stdout: Requirement already satisfied: six>=1.5 in /usr/local/lib/python3.10/dist-packages (from python-dateutil>=2.8.2->pandas) (1.16.0)
stdout: 要件はすでに満たされています: six>=1.5は/usr/local/lib/python3.10/dist-packagesにあります (python-dateutil>=2.8.2から->pandas) (1.16.0)

Additionally, you can download any file from the sandbox like this:
さらに、サンドボックスからファイルをこのようにダウンロードできます:
```

```md
# The path is a remote path in the sandbox
パスはサンドボックス内のリモートパスです。

```python
files_in_bytes = e2b_data_analysis_tool.download_file("/home/user/netflix.csv")
```

```python
files_in_bytes = e2b_data_analysis_tool.download_file("/home/user/netflix.csv")
```

最後に、run_commandを介してサンドボックス内で任意のシェルコマンドを実行できます。
Lastly, you can run any shell command inside the sandbox via run_command.

```

```md
# Install SQLitee2b_data_analysis_tool.run_command("sudo apt update")e2b_data_analysis_tool.install_system_packages("sqlite3")# Check the SQLite versionoutput = e2b_data_analysis_tool.run_command("sqlite3 --version")print("version: ", output["stdout"])print("error: ", output["stderr"])print("exit code: ", output["exit_code"])

# SQLiteのインストール
e2b_data_analysis_tool.run_command("sudo apt update")
e2b_data_analysis_tool.install_system_packages("sqlite3")

# SQLiteのバージョンを確認
output = e2b_data_analysis_tool.run_command("sqlite3 --version")
print("version: ", output["stdout"])
print("error: ", output["stderr"])
print("exit code: ", output["exit_code"])

stderr: stderr: WARNING: apt does not have a stable CLI interface. Use with caution in scripts.
stderr: stderr: 警告: aptには安定したCLIインターフェースがありません。スクリプトで使用する際は注意してください。

stdout: Hit:1 http://security.ubuntu.com/ubuntu jammy-security InReleasestdout: Hit:2 http://archive.ubuntu.com/ubuntu jammy InReleasestdout: Hit:3 http://archive.ubuntu.com/ubuntu jammy-updates InReleasestdout: Hit:4 http://archive.ubuntu.com/ubuntu jammy-backports InReleasestdout: Reading package lists...
stdout: stdout: ヒット:1 http://security.ubuntu.com/ubuntu jammy-security InRelease
stdout: ヒット:2 http://archive.ubuntu.com/ubuntu jammy
stdout: ヒット:3 http://archive.ubuntu.com/ubuntu jammy-updates
stdout: ヒット:4 http://archive.ubuntu.com/ubuntu jammy-backports
stdout: パッケージリストを読み込んでいます...

stdout: Building dependency tree...
stdout: 依存関係ツリーを構築しています...

stdout: Reading state information...
stdout: 状態情報を読み込んでいます...

stdout: All packages are up to date.
stdout: すべてのパッケージは最新です。

stdout: Reading package lists...
stdout: パッケージリストを読み込んでいます...

stdout: Building dependency tree...
stdout: 依存関係ツリーを構築しています...

stdout: Reading state information...
stdout: 状態情報を読み込んでいます...

stdout: Suggested packages:
stdout:   sqlite3-doc
stdout: 提案されたパッケージ:

stdout: The following NEW packages will be installed:
stdout: 次の新しいパッケージがインストールされます:

stdout:   sqlite3
stdout:   sqlite3

stdout: 0 upgraded, 1 newly installed, 0 to remove and 0 not upgraded.
stdout: 0がアップグレードされ、1が新たにインストールされ、0が削除され、0がアップグレードされません。

stdout: Need to get 768 kB of archives.
stdout: 768 kBのアーカイブを取得する必要があります。

stdout: After this operation, 1873 kB of additional disk space will be used.
stdout: この操作の後、1873 kBの追加ディスクスペースが使用されます。

stdout: Get:1 http://archive.ubuntu.com/ubuntu jammy-updates/main amd64 sqlite3 amd64 3.37.2-2ubuntu0.1 [768 kB]
stdout: 取得中:1 http://archive.ubuntu.com/ubuntu jammy-updates/main amd64 sqlite3 amd64 3.37.2-2ubuntu0.1 [768 kB]

stderr: debconf: delaying package configuration, since apt-utils is not installed
stderr: debconf: apt-utilsがインストールされていないため、パッケージ設定を遅延しています。

stdout: Fetched 768 kB in 0s (2258 kB/s)
stdout: 768 kBを0秒で取得しました (2258 kB/s)

stdout: Selecting previously unselected package sqlite3.
stdout: 以前選択されていなかったパッケージsqlite3を選択しています。

(stdout: (Reading database ... 23999 files and directories currently installed.)
stdout: (データベースを読み込んでいます ... 現在23999のファイルとディレクトリがインストールされています。)

stdout: Preparing to unpack .../sqlite3_3.37.2-2ubuntu0.1_amd64.deb ...
stdout: .../sqlite3_3.37.2-2ubuntu0.1_amd64.debの展開の準備をしています...

stdout: Unpacking sqlite3 (3.37.2-2ubuntu0.1) ...
stdout: sqlite3 (3.37.2-2ubuntu0.1)を展開しています...

stdout: Setting up sqlite3 (3.37.2-2ubuntu0.1) ...
stdout: sqlite3 (3.37.2-2ubuntu0.1)の設定を行っています...

stdout: 3.37.2 2022-01-06 13:25:41 872ba256cbf61d9290b571c0e6d82a20c224ca3ad82971edc46b29818d5dalt1
stdout: 3.37.2 2022-01-06 13:25:41 872ba256cbf61d9290b571c0e6d82a20c224ca3ad82971edc46b29818d5dalt1

version:  3.37.2 2022-01-06 13:25:41 872ba256cbf61d9290b571c0e6d82a20c224ca3ad82971edc46b29818d5dalt1
version:  3.37.2 2022-01-06 13:25:41 872ba256cbf61d9290b571c0e6d82a20c224ca3ad82971edc46b29818d5dalt1

error:  exit code:  0
error:  終了コード:  0

When your agent is finished, don't forget to close the sandbox
エージェントが終了したら、サンドボックスを閉じるのを忘れないでください。

e2b_data_analysis_tool.close()
e2b_data_analysis_tool.close()
```
