document.addEventListener('DOMContentLoaded', function() {
  // Lista de usuários simulada
  // Redireciona pela extensão do email
  function getPaginaPorEmail(email) {
  if (email.endsWith('@admin')) return 'PaginaAdminRelatorios.html';
  if (email.endsWith('@aluno')) return 'paginaaluno.html';
  if (email.endsWith('@professor')) return 'PaginaProfessorRelatorios.html';
    return null;
  }
  // Adiciona alerta customizado ao body
  var customAlert = document.createElement('div');
  customAlert.id = 'custom-alert';
  customAlert.style.display = 'none';
  customAlert.innerHTML = '<div id="custom-alert-title" style="font-size:1.3rem;margin-bottom:10px;"></div><span id="custom-alert-message"></span><br><button id="custom-alert-close">OK</button>';
  document.body.appendChild(customAlert);

  function showCustomAlert(message, title) {
    document.getElementById('custom-alert-title').textContent = title || 'Ação inválida';
    document.getElementById('custom-alert-message').textContent = message;
    customAlert.style.display = 'flex';
  }
  document.getElementById('custom-alert-close').onclick = function() {
    customAlert.style.display = 'none';
  };
  var forms = document.querySelectorAll('form');
  forms.forEach(function(form) {
    form.addEventListener('submit', function(e) {
      var senha = form.querySelector('input[type="password"]');
      var confirmarSenha = form.querySelector('#confirmar-senha');
      var senhaValor = senha ? senha.value : '';
      var confirmarValor = confirmarSenha ? confirmarSenha.value : senhaValor;
      var regex = /^(?=.[A-Z])(?=.\d)(?=.*[^A-Za-z0-9]).+$/;

      if (!regex.test(senhaValor)) {
        e.preventDefault();
        showCustomAlert('Sua senha deve conter pelo menos uma letra maiúscula, um número e um caractere especial (!, @, #, $ e %.).', 'Ação inválida');
      } else if (senhaValor !== confirmarValor) {
        e.preventDefault();
        showCustomAlert('As senhas não coincidem. Por favor, digite-as novamente.', 'Ação inválida');
      } else {
        // Verifica usuário na lista
        var emailInput = form.querySelector('input[type="email"]');
        var emailValor = emailInput ? emailInput.value : '';
        var pagina = getPaginaPorEmail(emailValor);
        if (!pagina) {
          e.preventDefault();
          showCustomAlert('Senha ou Email inválidos', 'Ação inválida');
        } else {
          e.preventDefault();
          showCustomAlert('Login realizado com sucesso!', 'Sucesso');
          setTimeout(function() {
            window.location.href = pagina;
          }, 1200);
        }
      }
    });
  });
});