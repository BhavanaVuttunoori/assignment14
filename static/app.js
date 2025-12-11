const API_URL = window.location.origin;
let token = localStorage.getItem('token');
let currentUser = null;

// Tab switching
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');
}

// Show message
function showMessage(elementId, message, isError = false) {
    const messageEl = document.getElementById(elementId);
    messageEl.textContent = message;
    messageEl.className = isError ? 'message error' : 'message success';
    messageEl.style.display = 'block';
    
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 5000);
}

// Register
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('auth-message', 'Registration successful! Please login.');
            showTab('login-tab');
            document.getElementById('register-form').reset();
        } else {
            showMessage('auth-message', data.detail || 'Registration failed', true);
        }
    } catch (error) {
        showMessage('auth-message', 'Network error: ' + error.message, true);
    }
});

// Login
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_URL}/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            token = data.access_token;
            localStorage.setItem('token', token);
            await loadUserInfo();
            showCalculationsSection();
            showMessage('calc-message', 'Login successful!');
            document.getElementById('login-form').reset();
        } else {
            showMessage('auth-message', data.detail || 'Login failed', true);
        }
    } catch (error) {
        showMessage('auth-message', 'Network error: ' + error.message, true);
    }
});

// Load user info
async function loadUserInfo() {
    try {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            document.getElementById('user-display').textContent = `Logged in as: ${currentUser.username}`;
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Show calculations section
function showCalculationsSection() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('calculations-section').classList.remove('hidden');
    loadCalculations();
}

// Logout
function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('calculations-section').classList.add('hidden');
    document.getElementById('calculations-list').innerHTML = '';
    showMessage('auth-message', 'Logged out successfully');
}

// Add calculation
document.getElementById('add-calculation-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const operation = document.getElementById('operation').value;
    const operand1 = parseFloat(document.getElementById('operand1').value);
    const operand2 = parseFloat(document.getElementById('operand2').value);
    
    // Validation
    if (!operation) {
        showMessage('calc-message', 'Please select an operation', true);
        return;
    }
    
    if (isNaN(operand1) || isNaN(operand2)) {
        showMessage('calc-message', 'Please enter valid numbers', true);
        return;
    }
    
    if (operation === 'divide' && operand2 === 0) {
        showMessage('calc-message', 'Cannot divide by zero', true);
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/calculations/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ operation, operand1, operand2 })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('calc-message', `Calculation created! Result: ${data.result}`);
            document.getElementById('add-calculation-form').reset();
            loadCalculations();
        } else {
            showMessage('calc-message', data.detail || 'Failed to create calculation', true);
        }
    } catch (error) {
        showMessage('calc-message', 'Network error: ' + error.message, true);
    }
});

// Load calculations (Browse)
async function loadCalculations() {
    try {
        const response = await fetch(`${API_URL}/calculations/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const calculations = await response.json();
        
        if (response.ok) {
            displayCalculations(calculations);
        } else {
            showMessage('calc-message', 'Failed to load calculations', true);
        }
    } catch (error) {
        showMessage('calc-message', 'Network error: ' + error.message, true);
    }
}

// Display calculations
function displayCalculations(calculations) {
    const listEl = document.getElementById('calculations-list');
    
    if (calculations.length === 0) {
        listEl.innerHTML = '<p style="text-align: center; color: #666; padding: 20px;">No calculations yet. Create your first calculation above!</p>';
        return;
    }
    
    listEl.innerHTML = calculations.map(calc => {
        const operationSymbol = {
            'add': '+',
            'subtract': '-',
            'multiply': '×',
            'divide': '÷'
        }[calc.operation];
        
        return `
            <div class="calculation-item">
                <div class="calculation-info">
                    <h3>${calc.operand1} ${operationSymbol} ${calc.operand2} = ${calc.result}</h3>
                    <p><strong>Operation:</strong> ${calc.operation}</p>
                    <p><strong>Created:</strong> ${new Date(calc.created_at).toLocaleString()}</p>
                    <p><strong>Updated:</strong> ${new Date(calc.updated_at).toLocaleString()}</p>
                </div>
                <div class="calculation-actions">
                    <button onclick="editCalculation(${calc.id})" class="btn btn-warning">Edit</button>
                    <button onclick="deleteCalculation(${calc.id})" class="btn btn-danger">Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

// Edit calculation
async function editCalculation(id) {
    try {
        const response = await fetch(`${API_URL}/calculations/${id}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const calc = await response.json();
        
        if (response.ok) {
            document.getElementById('edit-id').value = calc.id;
            document.getElementById('edit-operation').value = calc.operation;
            document.getElementById('edit-operand1').value = calc.operand1;
            document.getElementById('edit-operand2').value = calc.operand2;
            document.getElementById('edit-modal').classList.remove('hidden');
        } else {
            showMessage('calc-message', 'Failed to load calculation', true);
        }
    } catch (error) {
        showMessage('calc-message', 'Network error: ' + error.message, true);
    }
}

// Close edit modal
function closeEditModal() {
    document.getElementById('edit-modal').classList.add('hidden');
    document.getElementById('edit-calculation-form').reset();
}

// Submit edit
document.getElementById('edit-calculation-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const id = document.getElementById('edit-id').value;
    const operation = document.getElementById('edit-operation').value;
    const operand1 = parseFloat(document.getElementById('edit-operand1').value);
    const operand2 = parseFloat(document.getElementById('edit-operand2').value);
    
    // Validation
    if (isNaN(operand1) || isNaN(operand2)) {
        alert('Please enter valid numbers');
        return;
    }
    
    if (operation === 'divide' && operand2 === 0) {
        alert('Cannot divide by zero');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/calculations/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ operation, operand1, operand2 })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('calc-message', `Calculation updated! Result: ${data.result}`);
            closeEditModal();
            loadCalculations();
        } else {
            alert(data.detail || 'Failed to update calculation');
        }
    } catch (error) {
        alert('Network error: ' + error.message);
    }
});

// Delete calculation
async function deleteCalculation(id) {
    if (!confirm('Are you sure you want to delete this calculation?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/calculations/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            showMessage('calc-message', 'Calculation deleted successfully');
            loadCalculations();
        } else {
            const data = await response.json();
            showMessage('calc-message', data.detail || 'Failed to delete calculation', true);
        }
    } catch (error) {
        showMessage('calc-message', 'Network error: ' + error.message, true);
    }
}

// Check if already logged in
if (token) {
    loadUserInfo().then(() => {
        showCalculationsSection();
    });
}
