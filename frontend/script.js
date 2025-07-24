// Конфигурация API
const API_URL = '/api';
const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Глобальные переменные
let currentUserId = null;
let currentDepartmentId = null;

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
  // Инициализация Bootstrap компонентов
  const toastEl = document.getElementById('toast');
  const toast = new bootstrap.Toast(toastEl);
  
  // Переключение между разделами
  document.querySelectorAll('[data-section]').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const section = this.getAttribute('data-section');
      
      // Скрыть все разделы
      document.querySelectorAll('.section-content').forEach(el => {
        el.classList.add('d-none');
      });
      
      // Показать выбранный раздел
      document.getElementById(`${section}-section`).classList.remove('d-none');
      
      // Обновить активную ссылку в сайдбаре
      document.querySelectorAll('.nav-link').forEach(el => {
        el.classList.remove('active');
      });
      this.classList.add('active');
      
      // Загрузить данные при необходимости
      if (section === 'users') {
        loadUsers();
      } else if (section === 'departments') {
        loadDepartments();
      }
    });
  });
  
  // Показать/скрыть токен
  document.getElementById('toggle-token').addEventListener('click', function() {
    const tokenInput = document.getElementById('bot-token');
    const icon = this.querySelector('i');
    if (tokenInput.type === 'password') {
      tokenInput.type = 'text';
      icon.classList.remove('mdi-eye');
      icon.classList.add('mdi-eye-off');
    } else {
      tokenInput.type = 'password';
      icon.classList.remove('mdi-eye-off');
      icon.classList.add('mdi-eye');
    }
  });
  
  // Сохранить токен бота
  document.getElementById('token-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const token = document.getElementById('bot-token').value;
    
    axiosInstance.post('/config/bot-token', { token })
      .then(() => {
        showToast('Токен успешно сохранён', 'success');
      })
      .catch(error => {
        showToast('Ошибка при сохранении токена', 'danger');
        console.error('Ошибка токена:', error.response?.data || error.message);
      });
  });
  
  // Управление пользователями
  document.getElementById('save-user').addEventListener('click', saveUser);
  
  // Управление отделами
  document.getElementById('save-department').addEventListener('click', saveDepartment);
  
  // Загрузка PDF
  document.getElementById('upload-pdf').addEventListener('click', uploadPdf);
  
  // Загружаем отделы при открытии модалки пользователя
  document.getElementById('userModal').addEventListener('show.bs.modal', loadDepartmentsForSelect);
  
  // По умолчанию загружаем пользователей
  document.querySelector('[data-section="users"]').click();
});

// ==================== Функции для работы с пользователями ====================

function loadUsers() {
  axiosInstance.get('/users/')
    .then(response => {
      const tableBody = document.getElementById('users-table');
      tableBody.innerHTML = '';
      
      response.data.forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${user.telegram_id}</td>
          <td>${user.username || '-'}</td>
          <td>${user.role || '-'}</td>
          <td>${user.department || '-'}</td>
          <td>
            <i class="mdi mdi-pencil action-btn text-primary" data-id="${user.telegram_id}"></i>
            <i class="mdi mdi-delete action-btn text-danger" data-id="${user.telegram_id}"></i>
          </td>
        `;
        tableBody.appendChild(row);
      });
      
      // Назначить обработчики для кнопок
      document.querySelectorAll('.mdi-pencil').forEach(btn => {
        btn.addEventListener('click', editUser);
      });
      
      document.querySelectorAll('.mdi-delete').forEach(btn => {
        btn.addEventListener('click', deleteUser);
      });
    })
    .catch(error => {
      showToast('Ошибка при загрузке пользователей', 'danger');
      console.error('Ошибка загрузки пользователей:', error.response?.data || error.message);
    });
}

function editUser() {
  const telegramId = this.getAttribute('data-id');
  currentUserId = telegramId;
  
  axiosInstance.get(`/users/${telegramId}`)
    .then(response => {
      const user = response.data;
      document.getElementById('userModalTitle').textContent = 'Редактировать пользователя';
      document.getElementById('user-id').value = user.telegram_id;
      document.getElementById('telegram-id').value = user.telegram_id;
      document.getElementById('username').value = user.username || '';
      document.getElementById('role').value = user.role || '';
      
      // Установим значение отдела после загрузки списка
      const departmentSelect = document.getElementById('department');
      if (user.department && departmentSelect) {
        const option = Array.from(departmentSelect.options).find(opt => opt.value === user.department);
        if (option) option.selected = true;
      }
      
      const modal = new bootstrap.Modal(document.getElementById('userModal'));
      modal.show();
    })
    .catch(error => {
      showToast('Ошибка при загрузке данных пользователя', 'danger');
      console.error('Ошибка загрузки пользователя:', error.response?.data || error.message);
    });
}

function saveUser() {
  const userData = {
    telegram_id: parseInt(document.getElementById('telegram-id').value),
    username: document.getElementById('username').value,
    role: document.getElementById('role').value,
    department: document.getElementById('department').value
  };
  
  if (!userData.username || !userData.role || !userData.department) {
    showToast('Заполните все обязательные поля', 'warning');
    return;
  }
  
  const promise = currentUserId 
    ? axiosInstance.patch(`/users/${currentUserId}`, userData)
    : axiosInstance.post('/users/', userData);
  
  promise
    .then(() => {
      showToast('Пользователь сохранён', 'success');
      loadUsers();
      bootstrap.Modal.getInstance(document.getElementById('userModal')).hide();
      currentUserId = null;
    })
    .catch(error => {
      showToast('Ошибка при сохранении пользователя', 'danger');
      console.error('Ошибка сохранения пользователя:', error.response?.data || error.message);
    });
}

function deleteUser() {
  if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) return;
  
  const telegramId = this.getAttribute('data-id');
  
  axiosInstance.delete(`/users/${telegramId}`)
    .then(() => {
      showToast('Пользователь удалён', 'success');
      loadUsers();
    })
    .catch(error => {
      showToast('Ошибка при удалении пользователя', 'danger');
      console.error('Ошибка удаления пользователя:', error.response?.data || error.message);
    });
}

// ==================== Функции для работы с отделами ====================

function loadDepartments() {
  axiosInstance.get('/departments/')
    .then(response => {
      const tableBody = document.getElementById('departments-table');
      tableBody.innerHTML = '';
      
      response.data.forEach(dept => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${dept.id}</td>
          <td>${dept.name}</td>
          <td>${dept.description_for_ai || '-'}</td>
          <td>
            <i class="mdi mdi-pencil action-btn text-primary" data-id="${dept.id}"></i>
            <i class="mdi mdi-delete action-btn text-danger" data-id="${dept.id}"></i>
            <i class="mdi mdi-file-upload action-btn text-info" data-id="${dept.id}"></i>
          </td>
        `;
        tableBody.appendChild(row);
      });
      
      // Назначить обработчики для кнопок
      document.querySelectorAll('.mdi-pencil').forEach(btn => {
        btn.addEventListener('click', editDepartment);
      });
      
      document.querySelectorAll('.mdi-delete').forEach(btn => {
        btn.addEventListener('click', deleteDepartment);
      });
      
      document.querySelectorAll('.mdi-file-upload').forEach(btn => {
        btn.addEventListener('click', preparePdfUpload);
      });
    })
    .catch(error => {
      showToast('Ошибка при загрузке отделов', 'danger');
      console.error('Ошибка загрузки отделов:', error.response?.data || error.message);
    });
}

function loadDepartmentsForSelect() {
  return axiosInstance.get('/departments/')
    .then(response => {
      const select = document.getElementById('department');
      if (!select) return;
      
      select.innerHTML = '<option value="">Выберите отдел</option>';
      response.data.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.name;
        option.textContent = dept.name;
        select.appendChild(option);
      });
    })
    .catch(error => {
      console.error('Ошибка загрузки отделов для выбора:', error.response?.data || error.message);
    });
}

function editDepartment() {
  const departmentId = this.getAttribute('data-id');
  currentDepartmentId = departmentId;
  
  axiosInstance.get(`/departments/${departmentId}`)
    .then(response => {
      const dept = response.data;
      document.getElementById('departmentModalTitle').textContent = 
        currentDepartmentId ? 'Редактировать отдел' : 'Добавить отдел';
      document.getElementById('department-id').value = dept.id;
      document.getElementById('department-name').value = dept.name || '';
      document.getElementById('department-description').value = dept.description_for_ai || '';
      
      const modal = new bootstrap.Modal(document.getElementById('departmentModal'));
      modal.show();
    })
    .catch(error => {
      showToast('Ошибка при загрузке данных отдела', 'danger');
      console.error('Ошибка загрузки отдела:', error.response?.data || error.message);
    });
}

function saveDepartment() {
  const deptData = {
    name: document.getElementById('department-name').value,
    description_for_ai: document.getElementById('department-description').value || null
  };

  if (!deptData.name) {
    showToast('Название отдела обязательно', 'warning');
    return;
  }

  const method = currentDepartmentId ? 'patch' : 'post';
  const url = currentDepartmentId 
    ? `/departments/${currentDepartmentId}`
    : '/departments/';

  axiosInstance[method](url, deptData)
    .then(() => {
      showToast('Отдел сохранён', 'success');
      loadDepartments();
      bootstrap.Modal.getInstance(document.getElementById('departmentModal')).hide();
      currentDepartmentId = null;
    })
    .catch(error => {
      showToast('Ошибка при сохранении отдела', 'danger');
      console.error('Ошибка сохранения отдела:', error.response?.data || error.message);
    });
}

function deleteDepartment() {
  if (!confirm('Вы уверены, что хотите удалить этот отдел?')) return;
  
  const departmentId = this.getAttribute('data-id');
  
  axiosInstance.delete(`/departments/${departmentId}`)
    .then(() => {
      showToast('Отдел удалён', 'success');
      loadDepartments();
    })
    .catch(error => {
      showToast('Ошибка при удалении отдела', 'danger');
      console.error('Ошибка удаления отдела:', error.response?.data || error.message);
    });
}

// ==================== Функции для работы с PDF ====================

function preparePdfUpload() {
  currentDepartmentId = this.getAttribute('data-id');
  document.getElementById('current-department-id').value = currentDepartmentId;
  document.getElementById('pdf-file').value = '';
  
  const modal = new bootstrap.Modal(document.getElementById('pdfModal'));
  modal.show();
}

function uploadPdf() {
  const fileInput = document.getElementById('pdf-file');
  if (!fileInput.files.length) {
    showToast('Выберите файл для загрузки', 'warning');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  
  axiosInstance.post(`/departments/${currentDepartmentId}/upload-description/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  .then(() => {
    showToast('PDF успешно загружен', 'success');
    bootstrap.Modal.getInstance(document.getElementById('pdfModal')).hide();
  })
  .catch(error => {
    showToast('Ошибка при загрузке PDF', 'danger');
    console.error('Ошибка загрузки PDF:', error.response?.data || error.message);
  });
}

// ==================== Вспомогательные функции ====================

function showToast(message, type = 'success') {
  const toastEl = document.getElementById('toast');
  const toastMessage = document.getElementById('toast-message');
  
  toastMessage.textContent = message;
  toastEl.className = `toast align-items-center text-white bg-${type}`;
  
  const toast = new bootstrap.Toast(toastEl);
  toast.show();
}

// Очистка формы при закрытии модального окна
document.getElementById('userModal').addEventListener('hidden.bs.modal', function() {
  document.getElementById('user-form').reset();
  currentUserId = null;
});

document.getElementById('departmentModal').addEventListener('hidden.bs.modal', function() {
  document.getElementById('department-form').reset();
  currentDepartmentId = null;
});

// Инициализация новой модалки отдела
document.getElementById('departmentModal').addEventListener('show.bs.modal', function() {
  if (!currentDepartmentId) {
    document.getElementById('departmentModalTitle').textContent = 'Добавить отдел';
    document.getElementById('department-id').value = '';
  }
});