import tkinter as tk
from tkinter.simpledialog import askinteger, askstring
from tkinter import messagebox, Toplevel, Label, Scrollbar, Listbox
import pymongo
from datetime import datetime

# Conéctate a la base de datos MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["kol"]

# Definir las colecciones
users_collection = db["users"]
articles_collection = db["articles"]
comments_collection = db["comments"]
tags_collection = db["tags"]
categories_collection = db["categories"]

# Tkinter
root = tk.Tk()
root.title("Sistema de Gestión de Blog")

# Funciones CRUD para usuarios
def create_user(name, email):
    max_id = users_collection.find_one(sort=[("_id", pymongo.DESCENDING)])
    new_id = 1 if max_id is None else max_id["_id"] + 1

    user_data = {"_id": new_id, "name": name, "email": email}
    result = users_collection.insert_one(user_data)
    return result.inserted_id

def read_user():
    return users_collection.find()

def update_user(user_id, new_data):
    result = users_collection.update_one({"_id": user_id}, {"$set": new_data})
    return result.modified_count

def delete_user(user_id):
    result = users_collection.delete_one({"_id": user_id})
    return result.deleted_count

# Funciones CRUD para artículos
def create_article(user_id, title, date, text, tags, categories):
    max_id = articles_collection.find_one(sort=[("_id", pymongo.DESCENDING)])
    new_id = 1 if max_id is None else max_id["_id"] + 1

    article_data = {
        "_id": new_id,
        "user_id": user_id,
        "title": title,
        "date": date,
        "text": text,
        "tags": [],
        "categories": []
    }
    for tag_name in tags:
        existing_tag = tags_collection.find_one({"name": tag_name})
        if existing_tag:
            tag_id = existing_tag["_id"]
        else:
            tag_url = askstring("Agregar Artículo", f"URL para el tag {tag_name}:")
            tag_id = create_tag(tag_name, tag_url)
        article_data["tags"].append(tag_id)

    for category_name in categories:
        existing_category = categories_collection.find_one({"name": category_name})
        if existing_category:
            category_id = existing_category["_id"]
        else:
            category_url = askstring("Agregar Artículo", f"URL para la categoría {category_name}:")
            category_id = create_category(category_name, category_url)
        article_data["categories"].append(category_id)

    result = articles_collection.insert_one(article_data)

    for tag_id in article_data["tags"]:
        update_tag_articles(tag_id, result.inserted_id)

    for category_id in article_data["categories"]:
        update_category_articles(category_id, result.inserted_id)

    return result.inserted_id

def read_article():
    return articles_collection.find()

def update_article(article_id, new_data):
    result = articles_collection.update_one({"_id": article_id}, {"$set": new_data})
    
    if "tags" in new_data:
        tags = new_data["tags"]
        for tag_id in tags:
            update_tag(tag_id, {"$push": {"articles": article_id}})

    if "categories" in new_data:
        categories = new_data["categories"]
        for category_id in categories:
            update_category(category_id, {"$push": {"articles": article_id}})

    return result.modified_count

def delete_article(article_id):
    result = articles_collection.delete_one({"_id": article_id})
    return result.deleted_count

# Funciones CRUD para comentarios
def create_comment(user_id, article_id, name, url):
    max_id = comments_collection.find_one(sort=[("_id", pymongo.DESCENDING)])
    new_id = 1 if max_id is None else max_id["_id"] + 1

    comment_data = {"_id": new_id, "user_id": user_id, "article_id": article_id, "name": name, "url": url}
    result = comments_collection.insert_one(comment_data)
    return result.inserted_id

def read_comment():
    return comments_collection.find()

def update_comment(comment_id, new_data):
    result = comments_collection.update_one({"_id": comment_id}, {"$set": new_data})
    return result.modified_count

def delete_comment(comment_id):
    result = comments_collection.delete_one({"_id": comment_id})
    return result.deleted_count

# Funciones CRUD para tags
def create_tag(name, url):
    existing_tag = tags_collection.find_one({"name": name})
    if existing_tag:
        return existing_tag["_id"]
    
    max_id = tags_collection.find_one(sort=[("_id", pymongo.DESCENDING)])
    new_id = 1 if max_id is None else max_id["_id"] + 1

    tag_data = {"_id": new_id, "name": name, "url": url, "articles": []}
    result = tags_collection.insert_one(tag_data)
    return result.inserted_id

def read_tags():
    return tags_collection.find()

def update_tag(tag_id, new_name, new_url):
    result = tags_collection.update_one({"_id": tag_id}, {"$set": {"name": new_name, "url": new_url}})
    return result.modified_count

def delete_tag(tag_id):
    result = tags_collection.delete_one({"_id": tag_id})
    return result.deleted_count

# Funciones CRUD para categorías
def create_category(name, url):
    existing_category = categories_collection.find_one({"name": name})
    if existing_category:
        return existing_category["_id"]
    
    max_id = categories_collection.find_one(sort=[("_id", pymongo.DESCENDING)])
    new_id = 1 if max_id is None else max_id["_id"] + 1

    category_data = {"_id": new_id, "name": name, "url": url, "articles": []}
    result = categories_collection.insert_one(category_data)
    return result.inserted_id

def read_categories():
    return categories_collection.find()

def update_category(category_id, new_name, new_url):
    result = categories_collection.update_one({"_id": category_id}, {"$set": {"name": new_name, "url": new_url}})
    return result.modified_count

def delete_category(category_id):
    result = categories_collection.delete_one({"_id": category_id})
    return result.deleted_count

# Funciones extras para articles
def update_tag_articles(tag_id, article_id):
    tags_collection.update_one({"_id": tag_id}, {"$addToSet": {"articles": article_id}})

def update_category_articles(category_id, article_id):
    categories_collection.update_one({"_id": category_id}, {"$addToSet": {"articles": article_id}})

# Interfaz gráfica de usuario en Tkinter
def execute_action():
    selected_action = action_var.get()

    ###################  Usuarios  ########################
    if selected_action == "Agregar Usuario":
        name = askstring("Agregar Usuario", "Nombre:")
        if name is not None:
            email = askstring("Agregar Usuario", "Correo electrónico:")
            if email is not None:
                create_user(name, email)
                messagebox.showinfo("Notificación", "Usuario agregado correctamente.")
    
    elif selected_action == "Mostrar Usuarios":
        users_window = Toplevel(root)
        users_window.title("Usuarios")

        # Crear una lista para mostrar los usuarios
        user_listbox = Listbox(users_window, width=50, height=10, selectmode="extended")
        user_listbox.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Agregar barra de desplazamiento
        scrollbar = Scrollbar(users_window, orient="vertical")
        scrollbar.grid(row=0, column=2, sticky="ns")

        # Conectar la lista y la barra de desplazamiento
        user_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=user_listbox.yview)

        # Obtener usuarios y mostrar en la lista
        users = read_user()
        for user in users:
            user_listbox.insert("end", f"{user['name']} - {user['email']}")

    elif selected_action == "Actualizar Usuario":
        user_id = askinteger("Actualizar Usuario", "ID del usuario a actualizar:")
        if user_id is not None:
            new_name = askstring("Actualizar Usuario", "Nuevo nombre:")
            if new_name is not None:
                new_email = askstring("Actualizar Usuario", "Nuevo correo electrónico:")
                if new_email is not None:
                    update_user(user_id, {"name": new_name, "email": new_email})
                    messagebox.showinfo("Notificación", "Usuario actualizado correctamente.")

    elif selected_action == "Eliminar Usuario":
        user_id = askinteger("Eliminar Usuario", "ID del usuario a eliminar:")
        if user_id is not None:
            delete_user(user_id)
            messagebox.showinfo("Notificación", "Usuario eliminado correctamente.")

    ###################  Articulos  ########################
    elif selected_action == "Agregar Artículo":
        title = askstring("Agregar Artículo", "Título:")
        if title is not None:
            text = askstring("Agregar Artículo", "Texto:")
            if text is not None:
                user_id = askinteger("Agregar Artículo", "ID del usuario:")
                tags = askstring("Agregar Artículo", "Tags (separados por comas):").split(',')
                categories = askstring("Agregar Artículo", "Categorías (separadas por comas):").split(',')

                article_id = create_article(user_id, title, datetime.now(), text, tags, categories)

                messagebox.showinfo("Notificación", "Artículo agregado correctamente.")

    elif selected_action == "Mostrar Articulos":
        articles_window = Toplevel(root)
        articles_window.title("Articulos")

        # Crear una lista para mostrar los usuarios
        articles_listbox = Listbox(articles_window, width=50, height=10, selectmode="extended")
        articles_listbox.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Agregar barra de desplazamiento
        scrollbar = Scrollbar(articles_window, orient="vertical")
        scrollbar.grid(row=0, column=2, sticky="ns")

        # Conectar la lista y la barra de desplazamiento
        articles_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=articles_listbox.yview)

        # Obtener usuarios y mostrar en la lista
        articles = read_article()
        for article in articles:
            articles_listbox.insert("end", f"{article['title']} - {article['date']} - {article['text']}")

    elif selected_action == "Actualizar Artículo":
        article_id = askinteger("Actualizar Artículo", "ID del Artículo a actualizar:")
        if article_id is not None:
            new_title = askstring("Actualizar Artículo", "Nuevo título:")
            if new_title is not None:
                new_text = askstring("Actualizar Artículo", "Nuevo texto:")
                if new_text is not None:
                    new_tags = askstring("Actualizar Artículo", "Nuevos tags (separados por comas):").split(',')
                    new_categories = askstring("Actualizar Artículo", "Nuevas categorías (separadas por comas):").split(',')

                    update_data = {"title": new_title, "text": new_text, "tags": [], "categories": []}

                    for tag_name in new_tags:
                        tag_url = askstring("Actualizar Artículo", f"URL para el nuevo tag {tag_name}:")
                        tag_id = create_tag(tag_name, tag_url)
                        update_data["tags"].append(tag_id)

                    for category_name in new_categories:
                        category_url = askstring("Actualizar Artículo", f"URL para la nueva categoría {category_name}:")
                        category_id = create_category(category_name, category_url)
                        update_data["categories"].append(category_id)

                    update_article(article_id, update_data)
                    messagebox.showinfo("Notificación", "Artículo actualizado correctamente.")

    elif selected_action == "Eliminar Artículo":
        article_id = askinteger("Eliminar Artículo", "ID del Artículo a eliminar:")
        if article_id is not None:
            delete_article(article_id)
            messagebox.showinfo("Notificación", "Artículo eliminado correctamente.")

    ###################  Comentarios  ########################
    elif selected_action == "Agregar Comentario":
        user_id = askinteger("Agregar Comentario", "ID del usuario:")
        if user_id is not None:
            article_id = askinteger("Agregar Comentario", "ID del Artículo:")
            if article_id is not None:
                name = askstring("Agregar Comentario", "Nombre:")
                if name is not None:
                    url = askstring("Agregar Comentario", "URL:")
                    if url is not None:
                        create_comment(user_id, article_id, name, url)
                        messagebox.showinfo("Notificación", "Comentario agregado correctamente.")

    elif selected_action == "Mostrar Comentarios":
        comments_window = Toplevel(root)
        comments_window.title("Comentarios")

        # Crear una lista para mostrar los comentarios
        comments_listbox = Listbox(comments_window, width=50, height=10, selectmode="extended")
        comments_listbox.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Agregar barra de desplazamiento
        scrollbar = Scrollbar(comments_window, orient="vertical")
        scrollbar.grid(row=0, column=2, sticky="ns")

        # Conectar la lista y la barra de desplazamiento
        comments_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=comments_listbox.yview)

        # Obtener comentarios y mostrar en la lista
        comments = read_comment()
        for comment in comments:
            comments_listbox.insert("end", f"{comment['name']} - {comment['url']}")

    elif selected_action == "Actualizar Comentario":
        comment_id = askinteger("Actualizar Comentario", "ID del Comentario a actualizar:")
        if comment_id is not None:
            new_name = askstring("Actualizar Comentario", "Nuevo nombre:")
            if new_name is not None:
                new_url = askstring("Actualizar Comentario", "Nueva URL:")
                if new_url is not None:
                    update_comment(comment_id, {"name": new_name, "url": new_url})
                    messagebox.showinfo("Notificación", "Comentario actualizado correctamente.")

    elif selected_action == "Eliminar Comentario":
        comment_id = askinteger("Eliminar Comentario", "ID del Comentario a eliminar:")
        if comment_id is not None:
            delete_comment(comment_id)
            messagebox.showinfo("Notificación", "Comentario eliminado correctamente.")

    ###################  Tags  ########################
    elif selected_action == "Agregar Tag":
        name = askstring("Agregar Tag", "Nombre:")
        if name is not None:
            url = askstring("Agregar Tag", "URL:")
            if url is not None:
                create_tag(name, url)
                messagebox.showinfo("Notificación", "Tag agregado correctamente.")

    elif selected_action == "Mostrar Tags":
        tags_window = Toplevel(root)
        tags_window.title("Tags")

        # Crear una lista para mostrar los tags
        tags_listbox = Listbox(tags_window, width=50, height=10, selectmode="extended")
        tags_listbox.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Agregar barra de desplazamiento
        scrollbar = Scrollbar(tags_window, orient="vertical")
        scrollbar.grid(row=0, column=2, sticky="ns")

        # Conectar la lista y la barra de desplazamiento
        tags_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=tags_listbox.yview)

        # Obtener tags y mostrar en la lista
        tags = read_tags()
        for tag in tags:
            tags_listbox.insert("end", f"{tag['name']} - {tag['url']}")

    elif selected_action == "Actualizar Tag":
        tag_id = askinteger("Actualizar Tag", "ID del Tag a actualizar:")
        if tag_id is not None:
            new_name = askstring("Actualizar Tag", "Nuevo nombre:")
            if new_name is not None:
                new_url = askstring("Actualizar Tag", "Nueva URL:")
                if new_url is not None:
                    update_tag(tag_id, new_name, new_url)
                    messagebox.showinfo("Notificación", "Tag actualizado correctamente.")

    elif selected_action == "Eliminar Tag":
        tag_id = askinteger("Eliminar Tag", "ID del Tag a eliminar:")
        if tag_id is not None:
            delete_tag(tag_id)
            messagebox.showinfo("Notificación", "Tag eliminado correctamente.")

    ###################  Categories  ########################
    elif selected_action == "Agregar Categoria":
        name = askstring("Agregar Categoría", "Nombre:")
        if name is not None:
            url = askstring("Agregar Categoría", "URL:")
            if url is not None:
                create_category(name, url)
                messagebox.showinfo("Notificación", "Categoría agregada correctamente.")

    elif selected_action == "Mostrar Categorias":
        categories_window = Toplevel(root)
        categories_window.title("Categorias")

        # Crear una lista para mostrar las categorías
        categories_listbox = Listbox(categories_window, width=50, height=10, selectmode="extended")
        categories_listbox.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Agregar barra de desplazamiento
        scrollbar = Scrollbar(categories_window, orient="vertical")
        scrollbar.grid(row=0, column=2, sticky="ns")

        # Conectar la lista y la barra de desplazamiento
        categories_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=categories_listbox.yview)

        # Obtener categorías y mostrar en la lista
        categories = read_categories()
        for category in categories:
            categories_listbox.insert("end", f"{category['name']} - {category['url']}")

    elif selected_action == "Actualizar Categoria":
        category_id = askinteger("Actualizar Categoría", "ID de la Categoría a actualizar:")
        if category_id is not None:
            new_name = askstring("Actualizar Categoría", "Nuevo nombre:")
            if new_name is not None:
                new_url = askstring("Actualizar Categoría", "Nueva URL:")
                if new_url is not None:
                    update_category(category_id, new_name, new_url)
                    messagebox.showinfo("Notificación", "Categoría actualizada correctamente.")

    elif selected_action == "Eliminar Categoria":
        category_id = askinteger("Eliminar Categoría", "ID de la Categoría a eliminar:")
        if category_id is not None:
            delete_category(category_id)
            messagebox.showinfo("Notificación", "Categoría eliminada correctamente.")

# ComboBox
action_var = tk.StringVar(root)
action_var.set("Seleccione una acción")
actions = [
    "Agregar Usuario",
    "Mostrar Usuarios",
    "Actualizar Usuario",
    "Eliminar Usuario",
    "Agregar Artículo",
    "Mostrar Articulos",
    "Actualizar Artículo",
    "Eliminar Artículo",
    "Agregar Comentario",
    "Mostrar Comentarios",
    "Actualizar Comentario",
    "Eliminar Comentario",
    "Agregar Tag",
    "Mostrar Tags",
    "Actualizar Tag",
    "Eliminar Tag",
    "Agregar Categoria",
    "Mostrar Categorias",
    "Actualizar Categoria",
    "Eliminar Categoria"
]
action_combobox = tk.OptionMenu(root, action_var, *actions)
action_combobox.pack()

execute_button = tk.Button(root, text="Ejecutar Acción", command=execute_action)
execute_button.pack()

root.geometry("600x300")
root.geometry("+300+100")

root.mainloop()
