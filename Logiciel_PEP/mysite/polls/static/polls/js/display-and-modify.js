class DisplayEditForm extends HTMLElement {
    constructor(){
        super();
    }
    connectedCallback(){
        const shadow = this.attachShadow({mode : 'open'});
        // Add Bootstrap stylesheet to the shadow DOM
        const styleLink = document.createElement('link');
        styleLink.rel = 'stylesheet';
        styleLink.href = bootstrap;
        shadow.appendChild(styleLink);
        const card = document.createElement('div');
        card.classList.add("card", "shadow");
        const card_body = document.createElement('div');
        card_body.classList.add("card-body");
        const tab_content = document.createElement('div');
        tab_content.classList.add("tab-content");
        const list_group = document.createElement('ul');
        list_group.classList.add("list-group", "list-group-flush");
        const slot = document.createElement('slot');
        const text_right = document.createElement('div');
        text_right.classList.add("text-right");
        const modify_button = document.createElement('button');
        modify_button.classList.add('btn', 'btn-outline-secondary', 'mt-3');
        modify_button.textContent = "Modify";
        list_group.appendChild(slot);
        tab_content.appendChild(list_group);
        text_right.appendChild(modify_button);
        tab_content.appendChild(text_right);
        card_body.appendChild(tab_content);
        card.appendChild(card_body);
        shadow.appendChild(card);
    }

}

// Define the custom element
customElements.define('display-edit-form', DisplayEditForm);