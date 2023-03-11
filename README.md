# julia-package-universe

Download the package dependency graph of Julia's General registry for use in PubGrub.

## Introduction

This repository contains a Python sript to downlaod and process the package dependency graph of the 
[Julia General](https://github.com/JuliaRegistries/General) registry and save it in a JSON format that can be used as input to:
* the Dart implementation of the PubGrub version solver (see [dart-pubgrub-example](https://github.com/matlabpackages/dart-pubgrub-example))
* the MATLAB implementation of the PubGrub version solver

## Usage

Download a specific snapshot of the Julia registry given by a commit ID:

    git clone https://github.com/JuliaRegistries/General.git
    cd General
    git checkout 0acdcec7f51286bc286297576fd8c3218e298ea3
    cd ..

Install dependencies (requires [pdm](https://pdm.fming.dev)):

    pdm sync

Convert the dependency graph and save the output as JSON:

    pdm run python convert.py julia-packages.json

