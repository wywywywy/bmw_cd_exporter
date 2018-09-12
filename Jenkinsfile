pipeline {
  agent {
    docker {
      image 'python:3.6-slim'
      args '-v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker'
    }
  }
  options {
    buildDiscarder(
      logRotator(
        daysToKeepStr: '30',
        artifactDaysToKeepStr: '30'
      )
    )
  }
  stages {
    stage('Build Backend docker image') {
      steps {
        sh 'DATE=$(date +"%Y%m%d")'
        sh 'docker build -t wywywywy/bmw_cd_exporter:latest -t wywywywy/bmw_cd_exporter:$DATE .'
      }
    }
    stage('Push Backend docker image to repo') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerHub', passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
          sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPassword}"
          sh "docker push wywywywy/bmw_cd_exporter"
        }
      }
    }
  }
  post { 
    always {
    }
    success { 
    }
    unstable { 
    }
    failure { 
    }
    aborted { 
    }
  }
}