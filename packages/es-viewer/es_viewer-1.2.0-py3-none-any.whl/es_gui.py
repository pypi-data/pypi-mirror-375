# coding: utf-8
"""
A PyQt application to view and manage Elasticsearch with full CRUD operations,
HTTPS support, and corrected copy-paste functionality.
Author: isee15
Date: 2025-10-01
"""
import sys
import json
import os
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
import urllib3

# When choosing not to verify SSL certs, requests will print warnings. We disable them here.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QTreeView, QSplitter,
    QStatusBar, QMessageBox, QCheckBox, QFormLayout, QTabWidget, QMenu, QComboBox, QSizePolicy
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont, QKeySequence, QAction, QShortcut
from PyQt6.QtCore import Qt

# --- Config File Path ---
CONFIG_FILE = Path.home() / ".es_viewer_config.json"

# ==============================================================================
#  Business Logic Layer: Custom Elasticsearch Client
# ==============================================================================

class SimpleEsClientError(Exception):
    """Custom exception for client-side errors."""
    pass

class SimpleEsClient:
    """
    A minimal, handwritten Elasticsearch Python client.
    Supports HTTPS and SSL certificate verification control.
    """
    def __init__(self, base_url: str, auth: tuple = None, verify_ssl: bool = True):
        if base_url.endswith('/'): self.base_url = base_url[:-1]
        else: self.base_url = base_url
        self.auth = HTTPBasicAuth(auth[0], auth[1]) if auth else None
        self.headers = {"Content-Type": "application/json"}
        self.verify_ssl = verify_ssl

    def _make_request(self, method, endpoint, **kwargs):
        """Generic request handler."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(
                method=method, url=url, auth=self.auth, headers=self.headers,
                timeout=10, verify=self.verify_ssl, **kwargs
            )
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                 return {"acknowledged": True, "status": response.status_code, "operation": method}
            
            # Handle _cat API endpoints that return plain text
            if '_cat/' in endpoint:
                return {"text_response": response.text, "endpoint": endpoint, "status": response.status_code}
            
            # Try to parse as JSON, fallback to text if it fails
            try:
                return response.json()
            except json.JSONDecodeError:
                # If JSON parsing fails, return as text response
                return {"text_response": response.text, "endpoint": endpoint, "status": response.status_code}
                
        except requests.exceptions.HTTPError as e:
            error_details = f"HTTP Error: {e.response.status_code} {e.response.reason}"
            try:
                es_error_body = e.response.json()
                error_details += f"\nDetails: {json.dumps(es_error_body)}"
            except json.JSONDecodeError: 
                error_details += f"\nResponse Body: {e.response.text}"
            raise SimpleEsClientError(error_details) from e
        except requests.exceptions.SSLError as e:
            raise SimpleEsClientError(f"SSL Error: Could not verify certificate. Try unchecking 'Verify SSL Certificate'.\nDetails: {e}") from e
        except requests.exceptions.RequestException as e:
            raise SimpleEsClientError(f"Connection failed: {e}") from e

    def info(self): return self._make_request("GET", "")
    def search(self, index: str, query: dict): return self._make_request("POST", f"{index}/_search", json=query)
    def get_document(self, index: str, doc_id: str): return self._make_request("GET", f"{index}/_doc/{doc_id}")
    def get_mapping(self, index: str): return self._make_request("GET", f"{index}/_mapping")
    def custom_request(self, method: str, endpoint: str, body: dict = None):
        """Execute a custom HTTP request with any method and endpoint"""
        if body:
            return self._make_request(method.upper(), endpoint, json=body)
        else:
            return self._make_request(method.upper(), endpoint)
    def index_document(self, index: str, document: dict, doc_id: str = None):
        if doc_id: return self._make_request("PUT", f"{index}/_doc/{doc_id}", json=document)
        else: return self._make_request("POST", f"{index}/_doc", json=document)
    def update_document(self, index: str, doc_id: str, payload: dict): return self._make_request("POST", f"{index}/_update/{doc_id}", json=payload)
    def delete_document(self, index: str, doc_id: str): return self._make_request("DELETE", f"{index}/_doc/{doc_id}")

# ==============================================================================
#  UI Presentation Layer: PyQt Application
# ==============================================================================

class ElasticsearchViewer(QMainWindow):
    """
    A PyQt viewer for Elasticsearch with full CRUD, HTTPS, and corrected copy-paste support.
    """
    def __init__(self):
        super().__init__()
        self.es_client = None
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initializes the user interface."""
        self.setWindowTitle('ES Viewer v1.0(by isee15)')
        self.setGeometry(100, 100, 1280, 720)
        self.setMinimumSize(1024, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        connection_group = QWidget()
        connection_layout = QFormLayout(connection_group)
        connection_layout.setContentsMargins(0, 5, 0, 5)
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        self.index_input = QLineEdit()
        connection_layout.addRow('Host:', self.host_input)
        connection_layout.addRow('Port:', self.port_input)
        connection_layout.addRow('Index:', self.index_input)
        
        https_layout = QHBoxLayout()
        self.https_checkbox = QCheckBox('Use HTTPS')
        self.verify_ssl_checkbox = QCheckBox('Verify SSL Certificate')
        https_layout.addWidget(self.https_checkbox)
        https_layout.addWidget(self.verify_ssl_checkbox)
        connection_layout.addRow(https_layout)
        
        self.auth_checkbox = QCheckBox('Enable Authentication')
        connection_layout.addRow(self.auth_checkbox)
        self.user_label = QLabel('Username:')
        self.user_input = QLineEdit()
        self.pass_label = QLabel('Password:')
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        connection_layout.addRow(self.user_label, self.user_input)
        connection_layout.addRow(self.pass_label, self.pass_input)
        self.user_label.hide(); self.user_input.hide()
        self.pass_label.hide(); self.pass_input.hide()

        self.auth_checkbox.toggled.connect(self.toggle_auth_fields)
        self.https_checkbox.toggled.connect(self.toggle_ssl_verify_option)

        main_layout.addWidget(connection_group)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.tabs = QTabWidget()
        self.tab_search = QWidget()
        self.tab_document_editor = QWidget()
        self.tab_create_index = QWidget()
        self.tab_api_console = QWidget()

        self.tabs.addTab(self.tab_search, "🔍 Search")
        self.tabs.addTab(self.tab_document_editor, "📝 Document Editor")
        self.tabs.addTab(self.tab_create_index, "➕ Create Index")
        self.tabs.addTab(self.tab_api_console, "🚀 API Console")
        
        # ================= Search Tab =================
        search_layout = QVBoxLayout(self.tab_search)
        search_layout.setContentsMargins(10, 10, 10, 10)
        search_layout.addWidget(QLabel("<b>Query DSL</b>"))
        self.query_input = QTextEdit()
        self.query_input.setFont(QFont("Courier", 10))
        self.query_input.setMinimumHeight(100)
        search_layout.addWidget(self.query_input)
        self.execute_search_button = QPushButton('Search')
        self.execute_search_button.setSizePolicy(self.execute_search_button.sizePolicy().horizontalPolicy(), QSizePolicy.Policy.Fixed)
        self.execute_search_button.clicked.connect(self.execute_search)
        search_layout.addWidget(self.execute_search_button, 0, Qt.AlignmentFlag.AlignRight)

        # ================= Document Editor Tab =================
        crud_layout = QVBoxLayout(self.tab_document_editor)
        crud_layout.setContentsMargins(10, 10, 10, 10)
        crud_form_layout = QFormLayout()
        self.doc_id_input = QLineEdit()
        self.doc_id_input.setPlaceholderText("Optional for Create, required for others")
        crud_form_layout.addRow("Document ID:", self.doc_id_input)
        crud_layout.addLayout(crud_form_layout)
        crud_layout.addWidget(QLabel("<b>Document Source</b>"))
        self.doc_body_input = QTextEdit()
        self.doc_body_input.setFont(QFont("Courier", 10))
        self.doc_body_input.setMinimumHeight(100)
        crud_layout.addWidget(self.doc_body_input)
        button_layout = QHBoxLayout()
        self.get_button = QPushButton("Get")
        self.index_button = QPushButton("Create/Update")
        self.update_button = QPushButton("Partial Update")
        self.delete_button = QPushButton("Delete")
        button_layout.addWidget(self.get_button); button_layout.addWidget(self.index_button)
        button_layout.addWidget(self.update_button); button_layout.addWidget(self.delete_button)
        for button in [self.get_button, self.index_button, self.update_button, self.delete_button]:
            button.setSizePolicy(button.sizePolicy().horizontalPolicy(), QSizePolicy.Policy.Fixed)
        crud_layout.addLayout(button_layout)
        
        self.get_button.clicked.connect(self.execute_get)
        self.index_button.clicked.connect(self.execute_index)
        self.update_button.clicked.connect(self.execute_update)
        self.delete_button.clicked.connect(self.execute_delete)

        # ================= API Console Tab =================
        api_console_splitter = QSplitter(Qt.Orientation.Vertical)
        self.tab_api_console.setLayout(QVBoxLayout())
        self.tab_api_console.layout().addWidget(api_console_splitter)

        # Common APIs section
        common_api_widget = QWidget()
        quick_query_layout = QVBoxLayout(common_api_widget)
        quick_query_layout.setContentsMargins(5, 5, 5, 5)
        quick_query_layout.addWidget(QLabel("<b>Common APIs</b> (Double-click to run)"))
        
        self.quick_query_tree = QTreeView()
        self.quick_query_tree.setHeaderHidden(True)
        quick_query_model = QStandardItemModel()
        self.quick_query_tree.setModel(quick_query_model)
        self.populate_quick_query_tree(quick_query_model)
        self.quick_query_tree.expandAll()
        self.quick_query_tree.doubleClicked.connect(self.execute_quick_query)
        
        quick_query_layout.addWidget(self.quick_query_tree)
        api_console_splitter.addWidget(common_api_widget)

        # Custom Request section
        custom_request_widget = QWidget()
        custom_layout = QVBoxLayout(custom_request_widget)
        custom_layout.setContentsMargins(5, 10, 5, 5)
        custom_layout.addWidget(QLabel("<b>Custom Request</b>"))
        
        custom_form_layout = QFormLayout()
        self.http_method_combo = QComboBox()
        self.http_method_combo.addItems(["GET", "POST", "PUT", "DELETE", "HEAD", "PATCH"])
        self.http_endpoint_input = QLineEdit()
        self.http_endpoint_input.setPlaceholderText("e.g., _cat/nodes, my-index/_search")
        custom_form_layout.addRow("Method:", self.http_method_combo)
        custom_form_layout.addRow("Endpoint:", self.http_endpoint_input)
        custom_layout.addLayout(custom_form_layout)
        
        custom_layout.addWidget(QLabel("Request Body (JSON):"))
        self.custom_body_input = QTextEdit()
        self.custom_body_input.setFont(QFont("Courier", 10))
        self.custom_body_input.setPlaceholderText('{"query": {"match_all": {}}}')
        custom_layout.addWidget(self.custom_body_input)
        
        self.execute_custom_button = QPushButton('Execute')
        self.execute_custom_button.setSizePolicy(self.execute_custom_button.sizePolicy().horizontalPolicy(), QSizePolicy.Policy.Fixed)
        self.execute_custom_button.clicked.connect(self.execute_custom_request)
        custom_layout.addWidget(self.execute_custom_button, 0, Qt.AlignmentFlag.AlignRight)
        api_console_splitter.addWidget(custom_request_widget)
        api_console_splitter.setSizes([250, 250])


        # ================= Create Index Tab =================
        create_index_layout = QVBoxLayout(self.tab_create_index)
        create_index_layout.setContentsMargins(10, 10, 10, 10)
        
        # Basic Index Configuration
        basic_config_section = QWidget()
        basic_config_layout = QFormLayout(basic_config_section)
        basic_config_section.setStyleSheet("QWidget { border: 1px solid #ccc; border-radius: 5px; padding: 10px; }")
        
        self.new_index_name_input = QLineEdit()
        self.new_index_name_input.setPlaceholderText("e.g., my-new-index")
        basic_config_layout.addRow("Index Name:", self.new_index_name_input)
        
        shards_replicas_layout = QHBoxLayout()
        self.shards_input = QLineEdit("1")
        self.replicas_input = QLineEdit("1")
        shards_replicas_layout.addWidget(QLabel("Shards:"))
        shards_replicas_layout.addWidget(self.shards_input)
        shards_replicas_layout.addWidget(QLabel("Replicas:"))
        shards_replicas_layout.addWidget(self.replicas_input)
        basic_config_layout.addRow("Configuration:", shards_replicas_layout)
        
        create_index_layout.addWidget(basic_config_section)
        
        # Index Settings, Mappings, Aliases in a new Tab widget
        create_index_tabs = QTabWidget()
        
        # Settings Tab
        settings_tab = QWidget()
        settings_section_layout = QVBoxLayout(settings_tab)
        settings_section_layout.addWidget(QLabel("Define advanced index settings (e.g., analysis, refresh_interval)."))
        self.index_settings_input = QTextEdit()
        self.index_settings_input.setFont(QFont("Courier", 10))
        default_settings = {
            "analysis": {
                "analyzer": {
                    "default": {
                        "type": "standard"
                    }
                }
            }
        }
        self.index_settings_input.setPlainText(json.dumps(default_settings, indent=2))
        settings_section_layout.addWidget(self.index_settings_input)
        create_index_tabs.addTab(settings_tab, "⚙️ Settings")

        # Mappings Tab
        mappings_tab = QWidget()
        mappings_section_layout = QVBoxLayout(mappings_tab)
        mappings_section_layout.addWidget(QLabel("Define the schema for the index."))
        self.index_mappings_input = QTextEdit()
        self.index_mappings_input.setFont(QFont("Courier", 10))
        default_mappings = {
            "properties": {
                "title": {"type": "text"},
                "content": {"type": "text"},
                "created_at": {"type": "date"},
                "tags": {"type": "keyword"}
            }
        }
        self.index_mappings_input.setPlainText(json.dumps(default_mappings, indent=2))
        mappings_section_layout.addWidget(self.index_mappings_input)
        create_index_tabs.addTab(mappings_tab, "🗺️ Mappings")

        # Aliases Tab
        aliases_tab = QWidget()
        aliases_section_layout = QVBoxLayout(aliases_tab)
        aliases_section_layout.addWidget(QLabel("Define aliases for this index."))
        self.index_aliases_input = QTextEdit()
        self.index_aliases_input.setFont(QFont("Courier", 10))
        default_aliases = {"my-alias": {}}
        self.index_aliases_input.setPlaceholderText(json.dumps(default_aliases, indent=2))
        aliases_section_layout.addWidget(self.index_aliases_input)
        create_index_tabs.addTab(aliases_tab, "🔗 Aliases")

        create_index_layout.addWidget(create_index_tabs)
        
        # Action Buttons
        create_buttons_layout = QHBoxLayout()
        
        self.load_template_button = QPushButton('📄 Load Template')
        self.load_template_button.setToolTip('Load a predefined index template')
        self.load_template_button.clicked.connect(self.load_index_template)
        
        self.validate_config_button = QPushButton('✅ Validate')
        self.validate_config_button.setToolTip('Validate JSON configuration without creating the index')
        self.validate_config_button.clicked.connect(self.validate_index_config)
        
        self.create_index_button = QPushButton('Create Index')
        self.create_index_button.setToolTip('Create the index with specified configuration')
        self.create_index_button.clicked.connect(self.execute_create_index)
        self.create_index_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        
        for button in [self.load_template_button, self.validate_config_button, self.create_index_button]:
            button.setSizePolicy(button.sizePolicy().horizontalPolicy(), QSizePolicy.Policy.Fixed)

        create_buttons_layout.addWidget(self.load_template_button)
        create_buttons_layout.addWidget(self.validate_config_button)
        create_buttons_layout.addStretch()
        create_buttons_layout.addWidget(self.create_index_button)
        
        create_index_layout.addLayout(create_buttons_layout)

        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        results_layout.setContentsMargins(0, 5, 0, 0)
        
        # Add display mode toggle
        display_toggle_layout = QHBoxLayout()
        display_toggle_layout.addWidget(QLabel("Results:"))
        display_toggle_layout.addStretch()
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["JSON Text", "Tree View"])
        self.view_mode_combo.currentTextChanged.connect(self.toggle_display_mode)
        display_toggle_layout.addWidget(QLabel("Display Mode:"))
        display_toggle_layout.addWidget(self.view_mode_combo)
        results_layout.addLayout(display_toggle_layout)
        
        # JSON Text Display
        self.results_text = QTextEdit()
        self.results_text.setFont(QFont("Courier", 10))
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        # Tree View Display (initially hidden)
        self.results_tree = QTreeView()
        self.results_tree.hide()
        results_layout.addWidget(self.results_tree)
        
        main_splitter.addWidget(self.tabs)
        main_splitter.addWidget(results_widget)
        main_splitter.setSizes([550, 730])
        main_layout.addWidget(main_splitter)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.setup_copy_functionality()

    # --- Copy-Paste Functionality ---
    def setup_copy_functionality(self):
        self.results_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_tree.customContextMenuRequested.connect(self.open_tree_context_menu)
        copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self.results_tree)
        copy_shortcut.activated.connect(self.copy_selection_to_clipboard)
        
    def open_tree_context_menu(self, position):
        index = self.results_tree.indexAt(position)
        if index.isValid():
            menu = QMenu(); copy_action = QAction("Copy", self)
            copy_action.triggered.connect(self.copy_selection_to_clipboard); menu.addAction(copy_action)
            menu.exec(self.results_tree.viewport().mapToGlobal(position))

    def copy_selection_to_clipboard(self):
        """
        CORRECTED: Copies the key-value pair of the selected row to the clipboard.
        """
        selected_indexes = self.results_tree.selectionModel().selectedIndexes()
        if not selected_indexes:
            return

        # Get the index of the first selected cell to identify the row and parent
        selected_index = selected_indexes[0]
        model = self.results_tree.model()

        # Get the index for the key (column 0) of the selected row
        key_index = model.index(selected_index.row(), 0, selected_index.parent())
        key_text = model.data(key_index, Qt.ItemDataRole.DisplayRole)

        # Get the index for the value (column 1) of the selected row
        value_index = model.index(selected_index.row(), 1, selected_index.parent())
        value_text = model.data(value_index, Qt.ItemDataRole.DisplayRole)

        # Determine the final text to copy
        if value_text:
            # If there is a value, copy the full key-value pair
            text_to_copy = f"{key_text}: {value_text}"
        else:
            # If there's no value (it's a parent node), just copy the key
            text_to_copy = key_text
        
        if text_to_copy:
            QApplication.clipboard().setText(text_to_copy)
            self.status_bar.showMessage(f"Copied: '{text_to_copy}'", 3000)
            
    # --- Client and Settings Methods ---
    def _get_client(self):
        host = self.host_input.text().strip(); port = self.port_input.text().strip()
        if not host or not port:
            QMessageBox.warning(self, 'Input Error', 'Host and Port cannot be empty.')
            return None
        scheme = "https" if self.https_checkbox.isChecked() else "http"
        verify_ssl = self.verify_ssl_checkbox.isChecked()
        base_url = f"{scheme}://{host}:{port}"
        auth_tuple = None
        if self.auth_checkbox.isChecked():
            auth_tuple = (self.user_input.text(), self.pass_input.text())
        return SimpleEsClient(base_url=base_url, auth=auth_tuple, verify_ssl=verify_ssl)
        
    def save_settings(self):
        settings = {"host": self.host_input.text(), "port": self.port_input.text(), "index": self.index_input.text(), "https_enabled": self.https_checkbox.isChecked(), "verify_ssl": self.verify_ssl_checkbox.isChecked(), "auth_enabled": self.auth_checkbox.isChecked(), "username": self.user_input.text(), "password": self.pass_input.text(), "query": self.query_input.toPlainText()}
        try:
            with open(CONFIG_FILE, 'w') as f: json.dump(settings, f, indent=4)
        except IOError: pass

    def load_settings(self):
        default_query = {"query": {"match_all": {}}, "size": 10}
        default_update = {"doc": {"field_name": "new_value"}}
        if not os.path.exists(CONFIG_FILE):
            self.host_input.setText("localhost"); self.port_input.setText("9200"); self.index_input.setText("my-index")
            self.query_input.setText(json.dumps(default_query, indent=2))
            self.doc_body_input.setText(json.dumps(default_update, indent=2))
            self.verify_ssl_checkbox.setChecked(True)
            self.toggle_ssl_verify_option(self.https_checkbox.isChecked())
            return
        try:
            with open(CONFIG_FILE, 'r') as f: settings = json.load(f)
            self.host_input.setText(settings.get("host", "localhost")); self.port_input.setText(settings.get("port", "9200")); self.index_input.setText(settings.get("index", ""))
            self.https_checkbox.setChecked(settings.get("https_enabled", False)); self.verify_ssl_checkbox.setChecked(settings.get("verify_ssl", True))
            self.toggle_ssl_verify_option(self.https_checkbox.isChecked())
            self.auth_checkbox.setChecked(settings.get("auth_enabled", False))
            self.user_input.setText(settings.get("username", "")); self.pass_input.setText(settings.get("password", ""))
            self.query_input.setText(settings.get("query", json.dumps(default_query, indent=2)))
            self.doc_body_input.setText(json.dumps(default_update, indent=2))
        except (IOError, json.JSONDecodeError, KeyError): pass

    # --- Slots and Helper Methods ---
    def toggle_ssl_verify_option(self, checked):
        self.verify_ssl_checkbox.setVisible(checked)
    def toggle_auth_fields(self, checked):
        self.user_label.setVisible(checked); self.user_input.setVisible(checked)
        self.pass_label.setVisible(checked); self.pass_input.setVisible(checked)
    def execute_search(self):
        client = self._get_client(); index_name = self.index_input.text().strip()
        if not client or not index_name: QMessageBox.warning(self, 'Input Error', 'Host, Port, and Index are required.'); return
        try:
            query_json = json.loads(self.query_input.toPlainText())
            self.status_bar.showMessage(f'Executing search on index "{index_name}"...'); QApplication.processEvents()
            response = client.search(index=index_name, query=query_json)
            self.populate_tree(response); self.status_bar.showMessage('Search successful. Settings saved.', 5000); self.save_settings()
        except json.JSONDecodeError as e: QMessageBox.critical(self, 'JSON Error', f'Invalid JSON in query box:\n{e}')
        except SimpleEsClientError as e: QMessageBox.critical(self, 'Client Error', str(e))
    def execute_get(self):
        client = self._get_client(); index = self.index_input.text().strip(); doc_id = self.doc_id_input.text().strip()
        if not all([client, index, doc_id]): QMessageBox.warning(self, 'Input Error', 'Host, Port, Index and Document ID are required.'); return
        try:
            self.status_bar.showMessage(f"Getting document '{doc_id}'..."); response = client.get_document(index, doc_id)
            self.populate_tree(response); self.doc_body_input.setText(json.dumps(response.get("_source", {}), indent=2))
            self.status_bar.showMessage(f"Get document '{doc_id}' successful.", 5000)
        except SimpleEsClientError as e: QMessageBox.critical(self, 'Client Error', str(e))
    def execute_index(self):
        client = self._get_client(); index = self.index_input.text().strip(); doc_id = self.doc_id_input.text().strip() or None
        if not all([client, index]): QMessageBox.warning(self, 'Input Error', 'Host, Port, and Index are required.'); return
        try:
            doc_body = json.loads(self.doc_body_input.toPlainText())
            op_type = "Create" if doc_id is None else "Update"
            self.status_bar.showMessage(f"{op_type} document in '{index}'..."); response = client.index_document(index, doc_body, doc_id)
            self.populate_tree(response)
            if response.get("_id"): self.doc_id_input.setText(response["_id"])
            self.status_bar.showMessage(f"Document {op_type.lower()}d successfully.", 5000)
        except json.JSONDecodeError as e: QMessageBox.critical(self, 'JSON Error', f'Invalid JSON in document body:\n{e}')
        except SimpleEsClientError as e: QMessageBox.critical(self, 'Client Error', str(e))
    def execute_update(self):
        client = self._get_client(); index = self.index_input.text().strip(); doc_id = self.doc_id_input.text().strip()
        if not all([client, index, doc_id]): QMessageBox.warning(self, 'Input Error', 'Host, Port, Index and Document ID are required for partial update.'); return
        try:
            payload = json.loads(self.doc_body_input.toPlainText())
            if "doc" not in payload:
                QMessageBox.warning(self, 'Payload Error', 'Partial update payload must be wrapped in a "doc" object.')
                return
            self.status_bar.showMessage(f"Updating document '{doc_id}'..."); response = client.update_document(index, doc_id, payload)
            self.populate_tree(response); self.status_bar.showMessage(f"Update operation successful.", 5000)
        except json.JSONDecodeError as e: QMessageBox.critical(self, 'JSON Error', f'Invalid JSON in update payload:\n{e}')
        except SimpleEsClientError as e: QMessageBox.critical(self, 'Client Error', str(e))
    def execute_delete(self):
        client = self._get_client(); index = self.index_input.text().strip(); doc_id = self.doc_id_input.text().strip()
        if not all([client, index, doc_id]): QMessageBox.warning(self, 'Input Error', 'Host, Port, Index and Document ID are required.'); return
        confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete document '{doc_id}' from index '{index}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.No: return
        try:
            self.status_bar.showMessage(f"Deleting document '{doc_id}'..."); response = client.delete_document(index, doc_id)
            self.populate_tree(response); self.status_bar.showMessage(f"Delete operation successful.", 5000)
            self.doc_id_input.clear(); self.doc_body_input.clear()
        except SimpleEsClientError as e: QMessageBox.critical(self, 'Client Error', str(e))
    def execute_get_mapping(self):
        client = self._get_client(); index = self.index_input.text().strip()
        if not all([client, index]): QMessageBox.warning(self, 'Input Error', 'Host, Port, and Index are required.'); return
        try:
            self.status_bar.showMessage(f"Getting mapping for index '{index}'..."); QApplication.processEvents()
            response = client.get_mapping(index)
            self.populate_tree(response); self.status_bar.showMessage(f"Get mapping for index '{index}' successful.", 5000)
        except SimpleEsClientError as e: QMessageBox.critical(self, 'Client Error', str(e))
    
    def execute_mapping_operation(self, operation, method='GET', use_index=True):
        """Execute mapping-related operations with common error handling"""
        client = self._get_client()
        if not client:
            QMessageBox.warning(self, 'Input Error', 'Host and Port are required.')
            return
        
        if use_index:
            index = self.index_input.text().strip()
            if not index:
                QMessageBox.warning(self, 'Input Error', 'Index is required for this operation.')
                return
            endpoint = f"{index}/{operation}" if operation else index
        else:
            endpoint = operation
            
        try:
            self.status_bar.showMessage(f"Executing {method} {endpoint}...")
            QApplication.processEvents()
            
            if (method == 'HEAD'):
                # Special handling for HEAD requests
                response = client.custom_request(method, endpoint)
                # HEAD requests typically return empty body, so we create a status response
                response = {"exists": True, "status": response.get("status", 200), "endpoint": endpoint}
            else:
                response = client.custom_request(method, endpoint)
            
            self.populate_tree(response)
            self.status_bar.showMessage(f"{method} {endpoint} successful.", 5000)
        except SimpleEsClientError as e:
            if method == 'HEAD' and '404' in str(e):
                # Handle HEAD requests for non-existent resources
                response = {"exists": False, "status": 404, "endpoint": endpoint}
                self.populate_tree(response)
                self.status_bar.showMessage(f"Index does not exist.", 5000)
            else:
                QMessageBox.critical(self, 'Client Error', str(e))
    def execute_custom_request(self):
        client = self._get_client()
        if not client:
            QMessageBox.warning(self, 'Input Error', 'Host and Port are required.')
            return
        method = self.http_method_combo.currentText()
        endpoint = self.http_endpoint_input.text().strip()
        if not endpoint:
            QMessageBox.warning(self, 'Input Error', 'Endpoint is required.')
            return
        try:
            body = None
            if method in ["POST", "PUT", "PATCH"]:
                body = json.loads(self.custom_body_input.toPlainText())
            self.status_bar.showMessage(f"Executing custom request '{method} {endpoint}'...")
            response = client.custom_request(method, endpoint, body)
            self.populate_tree(response)
            self.status_bar.showMessage(f"Custom request '{method} {endpoint}' successful.", 5000)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, 'JSON Error', f'Invalid JSON in request body:\n{e}')
        except SimpleEsClientError as e:
            QMessageBox.critical(self, 'Client Error', str(e))
    def load_index_template(self):
        """Load predefined templates for different index types"""
        template_menu = QMenu(self)
        
        # Define templates
        templates = {
            "Document Store": {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1,
                    "analysis": {
                        "analyzer": {
                            "default": {
                                "type": "standard"
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "title": {"type": "text", "analyzer": "standard"},
                        "content": {"type": "text"},
                        "created_at": {"type": "date"},
                        "tags": {"type": "keyword"}
                    }
                },
                "aliases": {"documents": {}}
            },
            "Log Store": {
                "settings": {
                    "number_of_shards": 3,
                    "number_of_replicas": 0,
                    "index": {
                        "refresh_interval": "5s"
                    }
                },
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "message": {"type": "text"},
                        "source": {"type": "keyword"},
                        "host": {"type": "keyword"}
                    }
                },
                "aliases": {"logs": {}}
            },
            "Time Series": {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1,
                    "index": {
                        "sort.field": "timestamp",
                        "sort.order": "desc"
                    }
                },
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "metric_name": {"type": "keyword"},
                        "value": {"type": "double"},
                        "dimensions": {"type": "object"}
                    }
                },
                "aliases": {"metrics": {}}
            },
            "E-commerce": {
                "settings": {
                    "number_of_shards": 2,
                    "number_of_replicas": 1,
                    "analysis": {
                        "analyzer": {
                            "product_analyzer": {
                                "type": "standard",
                                "stopwords": "_english_"
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "name": {"type": "text", "analyzer": "product_analyzer"},
                        "description": {"type": "text"},
                        "price": {"type": "double"},
                        "category": {"type": "keyword"},
                        "brand": {"type": "keyword"},
                        "in_stock": {"type": "boolean"},
                        "created_date": {"type": "date"}
                    }
                },
                "aliases": {"products": {}}
            }
        }
        
        for template_name, template_config in templates.items():
            action = template_menu.addAction(f"📋 {template_name}")
            action.triggered.connect(lambda checked, config=template_config: self.apply_template(config))
        
        # Show menu at button position
        template_menu.exec(self.load_template_button.mapToGlobal(self.load_template_button.rect().bottomLeft()))

    def apply_template(self, template_config):
        """Apply a template configuration to the form fields"""
        try:
            # Update shards and replicas
            settings = template_config.get("settings", {})
            self.shards_input.setText(str(settings.get("number_of_shards", 1)))
            self.replicas_input.setText(str(settings.get("number_of_replicas", 1)))
            
            # Update settings (remove shards/replicas as they're handled separately)
            settings_copy = settings.copy()
            settings_copy.pop("number_of_shards", None)
            settings_copy.pop("number_of_replicas", None)
            self.index_settings_input.setPlainText(json.dumps(settings_copy, indent=2))
            
            # Update mappings
            mappings = template_config.get("mappings", {})
            self.index_mappings_input.setPlainText(json.dumps(mappings, indent=2))
            
            # Update aliases
            aliases = template_config.get("aliases", {})
            self.index_aliases_input.setPlainText(json.dumps(aliases, indent=2))
            
            self.status_bar.showMessage("Template loaded successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, 'Template Error', f'Failed to load template:\n{e}')

    def validate_index_config(self):
        """Validate the JSON configuration without creating the index"""
        try:
            # Validate index name
            index_name = self.new_index_name_input.text().strip()
            if not index_name:
                QMessageBox.warning(self, 'Validation Error', 'Index name is required.')
                return
            
            # Validate shards and replicas
            try:
                shards = int(self.shards_input.text())
                replicas = int(self.replicas_input.text())
                if shards < 1 or replicas < 0:
                    QMessageBox.warning(self, 'Validation Error', 'Shards must be >= 1, replicas must be >= 0.')
                    return
            except ValueError:
                QMessageBox.warning(self, 'Validation Error', 'Shards and replicas must be valid integers.')
                return
            
            # Validate JSON fields
            settings_text = self.index_settings_input.toPlainText().strip()
            if settings_text:
                json.loads(settings_text)
            
            mappings_text = self.index_mappings_input.toPlainText().strip()
            if mappings_text:
                json.loads(mappings_text)
            
            aliases_text = self.index_aliases_input.toPlainText().strip()
            if aliases_text:
                json.loads(aliases_text)
            
            QMessageBox.information(self, 'Validation Success', 'All configuration is valid! ✅')
            self.status_bar.showMessage("Configuration validated successfully", 3000)
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, 'JSON Validation Error', f'Invalid JSON:\n{e}')
        except Exception as e:
            QMessageBox.critical(self, 'Validation Error', f'Validation failed:\n{e}')

    def execute_create_index(self):
        """Create the index with the specified configuration"""
        client = self._get_client()
        if not client:
            QMessageBox.warning(self, 'Input Error', 'Host and Port are required.')
            return
        
        try:
            # Get and validate index name
            index_name = self.new_index_name_input.text().strip()
            if not index_name:
                QMessageBox.warning(self, 'Input Error', 'Index name is required.')
                return
            
            # Build the index configuration
            index_config = {}
            
            # Settings section
            settings = {}
            
            # Add shards and replicas
            try:
                shards = int(self.shards_input.text())
                replicas = int(self.replicas_input.text())
                if shards < 1 or replicas < 0:
                    QMessageBox.warning(self, 'Input Error', 'Shards must be >= 1, replicas must be >= 0.')
                    return
                settings["number_of_shards"] = shards
                settings["number_of_replicas"] = replicas
            except ValueError:
                QMessageBox.warning(self, 'Input Error', 'Shards and replicas must be valid integers.')
                return
            
            # Add custom settings
            settings_text = self.index_settings_input.toPlainText().strip()
            if settings_text:
                custom_settings = json.loads(settings_text)
                settings.update(custom_settings)
            
            index_config["settings"] = settings
            
            # Mappings section
            mappings_text = self.index_mappings_input.toPlainText().strip()
            if mappings_text:
                mappings = json.loads(mappings_text)
                index_config["mappings"] = mappings
            
            # Aliases section
            aliases_text = self.index_aliases_input.toPlainText().strip()
            if aliases_text:
                aliases = json.loads(aliases_text)
                index_config["aliases"] = aliases
            
            # Confirm creation
            confirm = QMessageBox.question(
                self, "Confirm Index Creation", 
                f"Are you sure you want to create index '{index_name}'?\n\n"
                f"Shards: {shards}, Replicas: {replicas}\n"
                f"This action cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.No:
                return
            
            # Create the index
            self.status_bar.showMessage(f"Creating index '{index_name}'...")
            QApplication.processEvents()
            
            response = client.custom_request("PUT", index_name, index_config)
            
            # Update the main index field with the newly created index
            self.index_input.setText(index_name)
            
            self.populate_tree(response)
            self.status_bar.showMessage(f"Index '{index_name}' created successfully!", 5000)
            
            QMessageBox.information(self, 'Success', f"Index '{index_name}' has been created successfully! 🎉")
            
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, 'JSON Error', f'Invalid JSON in configuration:\n{e}')
        except SimpleEsClientError as e:
            QMessageBox.critical(self, 'Creation Error', f'Failed to create index:\n{str(e)}')
        except Exception as e:
            QMessageBox.critical(self, 'Unexpected Error', f'An unexpected error occurred:\n{e}')
    def populate_tree(self, data):
        model = QStandardItemModel(); model.setHorizontalHeaderLabels(['Key', 'Value'])
        self.results_tree.setModel(model); root_item = model.invisibleRootItem()
        
        # Handle _cat API responses that return plain text
        if isinstance(data, dict) and 'text_response' in data:
            # Display formatted text response
            formatted_text = data['text_response']
            self.results_text.setPlainText(formatted_text)
            
            # Also create a tree view for the metadata
            self._populate_tree_model(data, root_item)
        else:
            # Normal JSON response handling
            self._populate_tree_model(data, root_item)
            self.results_text.setPlainText(json.dumps(data, indent=2))
        
        self.results_tree.expandToDepth(2)
    def _populate_tree_model(self, data, parent_item):
        if isinstance(data, dict):
            for key, value in data.items():
                key_item = QStandardItem(str(key)); key_item.setEditable(False)
                value_item = QStandardItem(); value_item.setEditable(False)
                parent_item.appendRow([key_item, value_item])
                if isinstance(value, (dict, list)): self._populate_tree_model(value, key_item)
                else: value_item.setText(str(value))
        elif isinstance(data, list):
            for index, value in enumerate(data):
                index_item = QStandardItem(f"[{index}]"); index_item.setEditable(False)
                value_item = QStandardItem(); value_item.setEditable(False)
                parent_item.appendRow([index_item, value_item])
                if isinstance(value, (dict, list)): self._populate_tree_model(value, index_item)
                else: value_item.setText(str(value))
    def toggle_display_mode(self, mode):
        if mode == "JSON Text":
            self.results_tree.hide()
            self.results_text.show()
        else:
            self.results_text.hide()
            self.results_tree.show()

    def populate_quick_query_tree(self, model):
        root_item = model.invisibleRootItem()

        # Cluster Operations
        cluster_category = QStandardItem("🌐 Cluster")
        cluster_category.setEditable(False)
        cluster_category.setSelectable(False)
        root_item.appendRow(cluster_category)
        
        queries_cluster = {
            "Cluster Health": {"endpoint": "_cluster/health", "method": "GET", "use_index": False},
            "Cluster Stats": {"endpoint": "_cluster/stats", "method": "GET", "use_index": False},
            "Node Stats": {"endpoint": "_nodes/stats", "method": "GET", "use_index": False},
            "List Nodes": {"endpoint": "_cat/nodes?v", "method": "GET", "use_index": False},
            "Pending Tasks": {"endpoint": "_cluster/pending_tasks", "method": "GET", "use_index": False},
        }
        for name, data in queries_cluster.items():
            item = QStandardItem(name)
            item.setData(data, Qt.ItemDataRole.UserRole)
            item.setEditable(False)
            cluster_category.appendRow(item)

        # Index Operations
        index_category = QStandardItem("📄 Indices")
        index_category.setEditable(False)
        index_category.setSelectable(False)
        root_item.appendRow(index_category)

        queries_indices = {
            "List All Indices": {"endpoint": "_cat/indices?v&s=index", "method": "GET", "use_index": False},
            "List All Mappings": {"endpoint": "_mapping", "method": "GET", "use_index": False},
            "List All Settings": {"endpoint": "_settings", "method": "GET", "use_index": False},
            "List All Aliases": {"endpoint": "_aliases", "method": "GET", "use_index": False},
        }
        for name, data in queries_indices.items():
            item = QStandardItem(name)
            item.setData(data, Qt.ItemDataRole.UserRole)
            item.setEditable(False)
            index_category.appendRow(item)

        # Current Index Operations
        current_index_category = QStandardItem("📝 Current Index")
        current_index_category.setEditable(False)
        current_index_category.setSelectable(False)
        root_item.appendRow(current_index_category)

        queries_current_index = {
            "Get Mapping": {"endpoint": "_mapping", "method": "GET", "use_index": True},
            "Get Settings": {"endpoint": "_settings", "method": "GET", "use_index": True},
            "Get Stats": {"endpoint": "_stats", "method": "GET", "use_index": True},
            "Check if Exists": {"endpoint": "", "method": "HEAD", "use_index": True},
            "Open Index": {"endpoint": "_open", "method": "POST", "use_index": True},
            "Close Index": {"endpoint": "_close", "method": "POST", "use_index": True},
            "Refresh Index": {"endpoint": "_refresh", "method": "POST", "use_index": True},
            "Force Merge": {"endpoint": "_forcemerge", "method": "POST", "use_index": True},
            "Clear Cache": {"endpoint": "_cache/clear", "method": "POST", "use_index": True},
        }
        for name, data in queries_current_index.items():
            item = QStandardItem(name)
            item.setData(data, Qt.ItemDataRole.UserRole)
            item.setEditable(False)
            current_index_category.appendRow(item)

    def execute_quick_query(self, index):
        item = self.quick_query_tree.model().itemFromIndex(index)
        if not item or not item.data(Qt.ItemDataRole.UserRole):
            return # Not a query item

        query_data = item.data(Qt.ItemDataRole.UserRole)
        self.execute_mapping_operation(
            operation=query_data["endpoint"],
            method=query_data["method"],
            use_index=query_data["use_index"]
        )

def main():
    app = QApplication(sys.argv)
    viewer = ElasticsearchViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()