param(
    [switch]$ListOnly
)

$ErrorActionPreference = 'Stop'

Set-Location (Join-Path $PSScriptRoot '..')

function Get-CurrentBranch {
    $branch = git branch --show-current 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw 'Not a git repository, or git is not available.'
    }

    return $branch.Trim()
}

function Get-BranchList {
    $branches = git for-each-ref --format='%(refname:short)' refs/heads 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw 'Failed to read local branches.'
    }

    return @($branches | Where-Object { $_ -and $_.Trim() } | ForEach-Object { $_.Trim() })
}

function Show-Menu {
    param(
        [string[]]$Items,
        [int]$SelectedIndex,
        [string]$CurrentBranch
    )

    Clear-Host
    Write-Host 'Git branch switcher'
    Write-Host ''
    Write-Host ('Current branch: ' + $CurrentBranch)
    Write-Host 'Use Up/Down to select, Enter to confirm, Esc to exit.'
    Write-Host ''

    for ($index = 0; $index -lt $Items.Count; $index++) {
        $prefix = '  '
        if ($index -eq $SelectedIndex) {
            $prefix = '> '
        }

        Write-Host ($prefix + $Items[$index])
    }
}

function Read-MenuSelection {
    param(
        [string[]]$Items,
        [string]$CurrentBranch
    )

    $selectedIndex = 0

    while ($true) {
        Show-Menu -Items $Items -SelectedIndex $selectedIndex -CurrentBranch $CurrentBranch
        $key = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

        switch ($key.VirtualKeyCode) {
            38 {
                if ($selectedIndex -gt 0) {
                    $selectedIndex--
                }
            }
            40 {
                if ($selectedIndex -lt ($Items.Count - 1)) {
                    $selectedIndex++
                }
            }
            13 {
                return $Items[$selectedIndex]
            }
            27 {
                return $null
            }
        }
    }
}

try {
    $currentBranch = Get-CurrentBranch
    $branches = Get-BranchList

    if ($ListOnly) {
        Write-Output ('Current branch: ' + $currentBranch)
        Write-Output 'Local branches:'
        $branches | ForEach-Object { Write-Output ('- ' + $_) }
        exit 0
    }

    $menuItems = @($branches) + '[Create new branch]' + '[Refresh branch list]'
    $choice = Read-MenuSelection -Items $menuItems -CurrentBranch $currentBranch

    if ($null -eq $choice) {
        Write-Host ''
        Write-Host 'Cancelled.'
        exit 0
    }

    if ($choice -eq '[Refresh branch list]') {
        & $PSCommandPath
        exit $LASTEXITCODE
    }

    if ($choice -eq '[Create new branch]') {
        Write-Host ''
        $newBranch = Read-Host 'New branch name'
        if ([string]::IsNullOrWhiteSpace($newBranch)) {
            throw 'Branch name cannot be empty.'
        }

        git checkout -b $newBranch
        if ($LASTEXITCODE -ne 0) {
            throw 'Failed to create and switch to the new branch.'
        }

        Write-Host ('Switched to new branch: ' + $newBranch)
        exit 0
    }

    git checkout $choice
    if ($LASTEXITCODE -ne 0) {
        throw ('Failed to switch to branch: ' + $choice)
    }

    Write-Host ('Switched to branch: ' + $choice)
    exit 0
}
catch {
    Write-Error $_
    exit 1
}