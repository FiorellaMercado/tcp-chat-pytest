# TDD: validación de mensajes

### RED

**Reglas (mensaje inválido):**
- Texto vacío, con solo espacios o tabulaciones.
- Texto de más de 200 caracteres.

 


**Tests que fallan:**
- `test_servidor_invalida_mensajes`: el servidor no debería enviarlos
  Resultado: 3 failed, el mensaje inválido llegó al receptor.
- `test_servidor_avisa_mensajes_invalidos`: el servidor debería avisar al emisor.
  Resultado: 3 failed, el emisor no recibió ningún aviso.

**Tests que pasan. Protegen la fase GREEN:**
- `test_servidor_valida_mensajes`: los mensajes válidos deben ser enviados por el servidor
  Resultado: 3 passed.


**Commit:** `2b26f00` test: add message validation tests (TDD red)

