# PyQt Elasticsearch Viewer
Elasticsearch ES可视化客户端工具

[下载地址](https://pan.quark.cn/s/ed38a68328eb)

*A simple, lightweight, cross-platform desktop GUI for browsing and managing Elasticsearch clusters.*

This tool is a self-contained desktop application built with Python and PyQt6. It provides a user-friendly interface for performing common Elasticsearch operations like searching, creating, reading, updating, and deleting documents. It is designed to be minimal and portable, relying only on the `requests` library for communication with Elasticsearch, with no dependency on the official `elasticsearch-py` client.

<img width="1800" height="1053" alt="image" src="https://github.com/user-attachments/assets/bc0f144a-ac04-4697-9c6f-22ccff585d0a" />

*(Note: Screenshot shows an earlier version; the final version includes more features like CRUD tabs and HTTPS options.)*

---

## ✨ Features

* **Flexible Connectivity**: Connect to any Elasticsearch cluster via HTTP or HTTPS.
* **Security Options**:
    * Support for username/password (Basic) authentication.
    * Option to disable SSL certificate verification for connecting to clusters with self-signed certificates.
* **Powerful Search**: A dedicated tab for writing and executing complex JSON-based Query DSL searches.
* **Full CRUD Functionality**: A "Document CRUD" tab for easy single-document operations:
    * **Get**: Retrieve a document by its ID.
    * **Index/Create**: Create or update a document. Supports both user-defined and auto-generated IDs.
    * **Update**: Partially update a document using the `_update` API.
    * **Delete**: Remove a document by its ID.
* **Interactive Results Display**: View results in a clear, expandable tree view that handles nested JSON structures gracefully.
* **User-Friendly**:
    * **Copy-Paste**: Easily copy keys, values, or full key-value pairs from the results tree with `Ctrl+C` or a right-click menu.
    * **Session Persistence**: Automatically saves your last successful connection and query configuration, loading it on the next launch.
* **Lightweight & Cross-Platform**:
    * Minimal dependencies: `PyQt6` and `requests`.
    * Runs on Windows, macOS, and Linux.

---

## 🛠️ Installation

You can install `es-viewer` directly from PyPI.

1.  **Install with pip:**
    Make sure you have Python 3 and pip installed, then run:
    ```bash
    pip install es-viewer
    ```

2.  **Run the application:**
    After installation, you can run the application from your terminal:
    ```bash
    es-viewer
    ```

### Alternative: Running from Source

If you prefer to run the application directly from the source code:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/isee15/es-viewer
    cd es-viewer
    ```

2.  **Install dependencies:**
    ```bash
    pip install PyQt6 requests
    ```

3.  **Run the application:**
    ```bash
    python es_gui.py
    ```

---

## 🚀 Usage

1.  **Run the application:**
    If you installed via pip, run `es-viewer` in your terminal. If running from source, use `python es_gui.py`.

2.  **Connection Panel:**
    * Fill in the `Host`, `Port`, and target `Index`.
    * Check **Use HTTPS** if your cluster uses SSL/TLS.
    * If using HTTPS with a self-signed certificate, you may need to uncheck **Verify SSL Certificate**.
    * Check **Enable Authentication** and fill in your credentials if your cluster requires them.

3.  **Search Tab:**
    * Write your full Elasticsearch Query DSL in the JSON editor.
    * Click **Execute Search** to run the query.
    * Results will be displayed in the tree view at the bottom.

4.  **Document CRUD Tab:**
    * **Document ID**: This field is required for `Get`, `Update`, and `Delete` operations. It is optional for `Index/Create` (if left blank, Elasticsearch will generate an ID).
    * **Document Body**:
        * For `Index/Create`, enter the full JSON content of the document.
        * For `Update`, enter an update payload (e.g., `{"doc": {"field_to_update": "new_value"}}`).
    * Click the corresponding button (`Get`, `Index/Create`, `Update`, `Delete`) to perform the action.
    * The result of the operation will be displayed in the tree view below.

---

## ⚙️ Configuration

The application automatically saves your settings to a configuration file upon a successful search operation.

* **File Location**: The file is named `.es_viewer_config.json` and is stored in your user home directory (e.g., `C:\Users\YourUser` on Windows or `/home/youruser` on Linux).
* **Function**: It stores the last used connection details, authentication state, and search query so you don't have to re-enter them every time you open the app.
* **Security Note**: The password is saved in plain text in this file. This is a security risk for production environments. Please use with caution.

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
