pipeline {
  agent {
    docker {
      image 'python:3.7-slim'
      args '-v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker'
    }
  }
  // triggers {
  //   cron('H 10 * * 2')
  // }
  // environment {
  //   XXX = 'xxx'
  // }
  options {
    buildDiscarder(
      logRotator(
        daysToKeepStr: '30',
        artifactDaysToKeepStr: '30'
      )
    )
  }
  stages {
    // stage('Init') {
    //   steps {
    //   }
    // }
    stage('Build Backend docker image') {
      steps {
        // sh 'DATE=$(date +"%Y%m%d")'
        // sh 'docker build -t wywywywy/bmw_cd_exporter:latest -t wywywywy/bmw_cd_exporter:$DATE .'
        sh """
          DATE=\$(date +"%Y%m%d")
          docker build -t wywywywy/bmw_cd_exporter:latest -t wywywywy/bmw_cd_exporter:\$DATE .
        """
      }
    }
    stage('Push Backend docker image to repo') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerHub', passwordVariable: 'dockerHubPassword', usernameVariable: 'dockerHubUser')]) {
          sh """
            DATE=\$(date +"%Y%m%d")
            docker login -u ${env.dockerHubUser} -p ${env.dockerHubPassword}
            docker push wywywywy/bmw_cd_exporter:\$DATE
            docker push wywywywy/bmw_cd_exporter:latest
          """
        }
      }
    }
  }
  // post { 
  //   always {
  //   }
  //   success { 
  //   }
  //   unstable { 
  //   }
  //   failure { 
  //   }
  //   aborted { 
  //   }
  // }
}