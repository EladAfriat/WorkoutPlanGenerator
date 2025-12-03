# 🌐 Load from URL - Feature Explanation

## What is "Load from URL"?

The **"Load from URL"** feature allows you to load exercise data from a web address instead of using the local file on your computer.

## Why Use It?

1. **Flexibility**: Update your exercise database without modifying code
2. **Sharing**: Share exercise data with others via a web link
3. **Updates**: Update exercises remotely - changes appear automatically
4. **Collaboration**: Multiple people can use the same exercise database

## How It Works

### Default Behavior (No URL)
- If you **leave the URL field empty**, the app uses the local file: `data/exercises.json`
- This is the default and works offline

### Using a URL
1. **Enter a URL** in the "Data URL" field in the sidebar
2. The URL should point to a JSON file with exercise data
3. Click **"🔄 Reload Data"** to load from the URL
4. The app will fetch and use that data instead of the local file

## Example URLs

### GitHub Raw URL
```
https://raw.githubusercontent.com/username/repo/main/data/exercises.json
```

### Any Web Server
```
https://yourserver.com/exercises.json
```

### JSON File Hosting
- Upload your `exercises.json` to any file hosting service
- Copy the direct link to the file
- Paste it in the URL field

## Format Required

The URL must point to a JSON file with the same structure as `data/exercises.json`:
- Exercise list with properties (name, muscle, level, equipment, etc.)
- Goal set/rep schemes
- Equipment options

## When to Use

✅ **Use URL when:**
- You want to update exercises frequently
- You're sharing the app with others
- You want centralized exercise data
- You're testing different exercise databases

❌ **Use local file when:**
- You're working offline
- You want guaranteed data availability
- You prefer local control
- You're developing/testing

## Important Notes

- The URL must be publicly accessible (no login required)
- The file must be valid JSON format
- If the URL fails, the app will show an error
- You can switch back to local file by clearing the URL field and reloading

## Current Status

- **Empty URL field** = Using local `data/exercises.json` file
- **URL entered** = Will load from that web address (click "Reload Data" to apply)

