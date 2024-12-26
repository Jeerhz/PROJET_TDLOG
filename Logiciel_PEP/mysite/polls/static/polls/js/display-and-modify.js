//////////// HOW TO USE ////////////
/*
<display-edit-form
        save-url="{% url 'save_changes'%}"
        data-items='[
        {"label": "Name", name="student-name", "value": "John Doe"},
        {"label": "Email", name="student-email", "value": "john@example.com"},
        {"label": "Phone", name="student-phone", "value": "+1234567890"}
        ]'>
        {% csrf_token %}
</display-edit-form>
*/
////////////////////////////////////

class DisplayEditForm extends HTMLElement {
    constructor() {
        super();
        this.isEditMode = false;
    }

    // Observe these attributes for changes
    static get observedAttributes() {
        return ['data-items'];
    }

    connectedCallback() {
        this.render();
        this.attachEventListeners();
    }

    // Convert the data-items string to an array of objects
    get items() {
        try {
            return JSON.parse(this.getAttribute('data-items'));
        } catch {
            return [];
        }
    }

    attachEventListeners() {
        const editButton = this.querySelector('.edit-button');
        const saveButton = this.querySelector('.save-button');
        const cancelButton = this.querySelector('.cancel-button');

        editButton?.addEventListener('click', () => this.toggleEditMode());
        saveButton?.addEventListener('click', () => this.saveChanges());
        cancelButton?.addEventListener('click', () => this.cancelEdit());
    }

    toggleEditMode() {
        this.isEditMode = !this.isEditMode;
        this.render();
    }

    async saveChanges() {
        const form = this.querySelector('form');
        const formData = new FormData(form);
        const updatedItems = this.items.map((item, index) => ({
            name: item.name,
            value: formData.get(item.name)
        }));

        try {
            const response = await fetch(this.getAttribute('save-url'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(updatedItems)
            });

            if (!response.ok) throw new Error('Save failed');

            const data = await response.json();
            this.setAttribute('data-items', JSON.stringify(data));
            this.isEditMode = false;
            this.render();
        } catch (error) {
            console.error('Save failed:', error);
            alert('Failed to save changes');
        }
    }

    cancelEdit() {
        this.isEditMode = false;
        this.render();
    }

    render() {
        const items = this.items;
        
        this.innerHTML = `
            <div class="card shadow">
                <div class="card-body">
                    ${this.isEditMode ? this.renderEditMode(items) : this.renderDisplayMode(items)}
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    renderDisplayMode(items) {
        return `
            <dl class="row mb-0">
                ${items.map(item => `
                    <dt class="col-sm-3">${item.label}</dt>
                    <dd class="col-sm-9">${item.value}</dd>
                `).join('')}
            </dl>
            <div class="text-end mt-3">
                <button type="button" class="btn btn-outline-secondary mt-3 edit-button">
                    <i class="bi bi-pencil"></i> Modify
                </button>
            </div>
        `;
    }

    renderEditMode(items) {
        return `
            <form>
                ${items.map((item, index) => `
                    <div class="mb-3 row">
                        <label class="col-sm-3 col-form-label">${item.label}</label>
                        <div class="col-sm-9">
                            <input type="text" 
                                   class="form-control" 
                                   name="${item.name}" 
                                   value="${item.value}">
                        </div>
                    </div>
                `).join('')}
                <div class="row justify-content-between mt-3">
                    <div class="col-auto">
                        <button type="button" class="btn btn-outline-secondary mt-3 cancel-button">Cancel</button>
                    </div>
                    <div class="col-auto">
                        <button type="button" class="btn btn-outline-success mt-3 save-button">Save</button>
                    </div>
                </div>
            </form>
        `;
    }
}

// Register the custom element
customElements.define('display-edit-form', DisplayEditForm);