if __name__ == "__main__":
    import yphapp
    app = yphapp.create_app('development')
    app.run(host='0.0.0.0', port=443)
